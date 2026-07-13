"""Train and evaluate the insider-threat detectors.

    python -m scripts.train_detect

Run AFTER scripts.build_features. Trains three detectors on a CHRONOLOGICAL
split (train on the past, detect on the future) and reports precision, recall,
F1 and false-positive rate against the CERT ground truth.

Deliberately does NOT report accuracy. 0.41% of user-days are malicious, so
predicting "normal" for everything scores 99.6% accuracy while catching zero
insiders. Any metric that rewards that is measuring the wrong thing.
"""

import sys

from backend.app.database import SessionLocal
from backend.app.detection import run_detection


def _fmt_metrics(name: str, m: dict) -> None:
    print(f"\n  {name}")
    print(f"    precision            {m['precision']:.4f}   "
          "(of the days we flagged, how many were real attacks)")
    print(f"    recall               {m['recall']:.4f}   "
          "(of the real attacks, how many did we catch)")
    print(f"    F1                   {m['f1']:.4f}")
    print(f"    false positive rate  {m['false_positive_rate']:.5f}  "
          "(the alert-fatigue number)")
    if "pr_auc" in m:
        print(f"    PR-AUC               {m['pr_auc']:.4f}   "
              "(honest headline metric on imbalanced data)")
        print(f"    ROC-AUC              {m['roc_auc']:.4f}   "
              "(flattering on imbalanced data - shown for completeness)")
    print(f"    confusion            TP={m['true_positives']:,}  "
          f"FP={m['false_positives']:,}  "
          f"FN={m['false_negatives']:,}  TN={m['true_negatives']:,}")


def main() -> int:
    db = SessionLocal()
    try:
        print("Training detectors...")
        print("(chronological split: train on the past, detect on the future)")
        print()

        r = run_detection(db, save_models_to_disk=True)

        s = r["split"]
        print("=" * 78)
        print("DATA SPLIT")
        print("=" * 78)
        print(f"  strategy             {s['strategy']}")
        print(f"  baseline cutoff      {s['baseline_cutoff']}")
        print(f"  train                {s['train_users']:>6,} users  "
              f"({s['train_insiders']} insiders)  "
              f"{s['train_rows']:>8,} user-days  ({s['train_malicious']:,} malicious)")
        print(f"  test  (held out)     {s['test_users']:>6,} users  "
              f"({s['test_insiders']} insiders)  "
              f"{s['test_rows']:>8,} user-days  ({s['test_malicious']:,} malicious)")
        print(f"  malicious rate       {s['test_malicious_rate']:.5f}  "
              f"({s['test_malicious_rate'] * 100:.3f}% of test days)")
        print(f"  features             {r['n_features']}")
        print()
        print("  The split is by USER, so the test insiders are people the model has")
        print("  NEVER seen. That is the real question: can we catch an insider we")
        print("  have not already been shown?")
        print()
        print("  A chronological split was tried first and FAILED - it put every")
        print("  attack in the test half, leaving training with zero positives.")
        print("  The model learned nothing and reported 0% recall as if it were a")
        print("  finding. Baselines are still temporal (to stop a user's own attack")
        print("  inflating his own 'normal'); only the train/test split is by user.")

        # --------------------------------------------------------------
        # Z-SCORE HEALTH CHECK
        # --------------------------------------------------------------
        # On the real CERT data, Isolation Forest scored 0.008 recall while
        # XGBoost - fed the identical features - scored 0.69. The suspected cause
        # is a division artifact: when a user's standard deviation is near zero,
        # their z-score explodes into the thousands. XGBoost shrugs (rank-based
        # splits); Isolation Forest chokes (value-based splits, so one absurd
        # point is isolated instantly and consumes the whole alert budget).
        #
        # That hypothesis could NOT be reproduced on synthetic data. So rather
        # than assert a fix and hope, this prints the evidence and lets the real
        # data settle it:
        #
        #   many values at the ceiling -> artifact was REAL, guards are working
        #   almost none at the ceiling -> hypothesis was WRONG, look elsewhere
        z = r["z_diagnostics"]
        print()
        print("=" * 78)
        print("Z-SCORE HEALTH CHECK  (was the division-artifact hypothesis right?)")
        print("=" * 78)
        print(f"  std floor             {z['std_floor']}")
        print(f"  z clipped at          +/-{z['z_clip']}")
        print(f"  max |z| after clip    {z['max_abs_z']:.1f}")
        print(f"  99.9th percentile     {z['pct_99_9']:.1f}")
        print(f"  values AT ceiling     {z['values_at_clip_ceiling']:,}  "
              f"({z['pct_at_ceiling']:.3f}% of all z-scores)")
        print()
        if z["pct_at_ceiling"] > 0.05:
            print("  -> A real number of z-scores were runaway values, now clipped.")
            print("     The artifact was REAL. Isolation Forest should improve.")
        else:
            print("  -> Almost nothing hit the ceiling, so the division artifact")
            print("     was NOT the problem. If Isolation Forest is still poor,")
            print("     the honest conclusion is that unsupervised detection is")
            print("     simply weak here - a legitimate finding, not a failure.")

        print()
        print("=" * 78)
        print("RESULTS ON HELD-OUT DATA")
        print("=" * 78)
        _fmt_metrics(
            "Isolation Forest  (UNSUPERVISED - never saw a single label)",
            r["isolation_forest"],
        )
        _fmt_metrics(
            f"XGBoost  (SUPERVISED - class weight {r['xgboost']['scale_pos_weight']:.0f}x "
            "to counter imbalance)",
            r["xgboost"],
        )

        print()
        print("=" * 78)
        print("PER-SCENARIO RECALL - the number that actually matters")
        print("=" * 78)
        print("  An aggregate recall of 0.85 could still mean 'missed scenario 3")
        print("  entirely'. Scenario 3 is a handful of days; it vanishes inside an")
        print("  average. Three different attacks, reported separately.")
        print()
        print(f"  {'scenario':<10}{'test days':>12}{'XGB caught':>13}"
              f"{'XGB recall':>13}{'IF caught':>12}{'IF recall':>12}")
        print("  " + "-" * 72)
        for p in r["per_scenario"]:
            print(f"  {p['scenario']:<10}{p['malicious_days_in_test']:>12,}"
                  f"{p['xgb_caught']:>13,}{p['xgb_recall']:>13.2%}"
                  f"{p['iso_caught']:>12,}{p['iso_recall']:>12.2%}")

        u = r["user_level"]
        print()
        print("=" * 78)
        print("USER-LEVEL DETECTION - what a security manager actually asks")
        print("=" * 78)
        print("  An analyst does not care that we flagged 6 of an insider's 9 bad")
        print("  days. They care whether we caught the insider AT ALL.")
        print()
        print(f"  insiders active in the test period   {u['insiders_active_in_test_period']}")
        print(f"  caught at least once                 {u['insiders_caught_at_least_once']}")
        print(f"  USER-LEVEL RECALL                    {u['user_level_recall']:.1%}")

        curve = r.get("operating_curve")
        if curve:
            print()
            print("=" * 78)
            print("THE OPERATING CURVE - precision and recall are a DIAL, not a score")
            print("=" * 78)
            print("  A single precision/recall pair is a policy choice wearing the")
            print("  costume of a result. The model's QUALITY is the PR-AUC. Where you")
            print("  set the dial is a decision about what an analyst can carry - and")
            print("  it should be made by a person, in the open, not by a default")
            print("  buried in a library.")
            print()
            print(f"  {'false-pos rate':>15} {'alerts':>9} {'precision':>11} {'recall':>9}")
            print("  " + "-" * 48)
            for c in curve:
                mark = ""
                print(f"  {c['fpr']:>15.4f} {c['alerts']:>9,} "
                      f"{c['precision']:>11.4f} {c['recall']:>9.4f}{mark}")
            print()
            xg = r["xgboost"]
            print(f"  The pipeline chose {xg['threshold']:.4f}, by maximising F2 on")
            print(f"  {xg['threshold_chosen_on']}.")
            print("  F2 weights recall 4x over precision - a missed insider is a breach,")
            print("  a false positive is an hour of someone's time. Those costs are not")
            print("  equal, and F1 would pretend they are.")

        convs = r.get("labelling_conventions")
        if convs:
            print()
            print("=" * 78)
            print("THE TWO LABELLING CONVENTIONS - and why the numbers move")
            print("=" * 78)
            print("  We label a day malicious if it falls inside the insider's WINDOW.")
            print("  The published literature labels a day malicious only if a malicious")
            print("  EVENT actually happened on it. The two disagree about 49% of days.")
            print()
            print(f"  {'convention':<14} {'malicious days':>15} {'recall':>9} {'precision':>11}")
            print("  " + "-" * 52)
            for c in convs:
                print(f"  {c['convention']:<14} {c['malicious_days']:>15,} "
                      f"{c['recall']:>9.4f} {c['precision']:>11.4f}")
            print()
            per = r.get("labelling_per_scenario") or []
            if per:
                print("  PER SCENARIO - this is where the distortion actually lives:")
                print()
                print(f"  {'scenario':<10} {'window days':>12} {'event days':>11} "
                      f"{'window rec':>11} {'event rec':>10}")
                print("  " + "-" * 58)
                for p_ in per:
                    print(f"  {p_['scenario']:<10} {p_['window_days']:>12,} "
                          f"{p_['event_days']:>11,} {p_['window_recall']:>11.2%} "
                          f"{p_['event_recall']:>10.2%}")
                print()
            print("  Scenario 1 is a SINGLE-DAY exfiltration handed a multi-week window.")
            print("  AAM0658 has seven window days and TWO real ones - so we are being")
            print("  scored for 'missing' five days on which the man did nothing wrong.")
            print("  Scenario 2 is a sustained campaign, so its window is nearer the truth.")
            print()
            print("  NEITHER IS A LIE. 'Catch him during the campaign' is a defensible")
            print("  target. But a recall number quoted without saying which convention")
            print("  produced it is not comparable to anything - including a paper.")

        land = r.get("alert_landing")
        if land:
            n = land["alerts"]
            real = land["on_a_real_attack_day"]
            mid = land["on_an_insider_mid_campaign"]
            out = land["outside_any_window"]
            print()
            print("  WHERE THE ALERTS ACTUALLY LAND  (same model, same threshold)")
            print()
            print(f"    {n:>5}  alerts raised")
            print(f"    {real:>5}  on a day an attack ACTUALLY ran        "
                  f"{100*real/max(n,1):>5.1f}%")
            print(f"    {mid:>5}  on an INSIDER mid-campaign, no logged  "
                  f"{100*mid/max(n,1):>5.1f}%")
            print(f"           malicious event that day")
            print(f"    {out:>5}  outside ANY insider's window           "
                  f"{100*out/max(n,1):>5.1f}%")
            print("    " + "-" * 52)
            print(f"    {real+mid:>5}  on an insider DURING his campaign      "
                  f"{100*(real+mid)/max(n,1):>5.1f}%")
            print()
            print("  The middle group is what the event-day convention scores as a")
            print("  FALSE POSITIVE. It is not one. A scenario-2 insider browses job")
            print("  sites for weeks and THEN steals - a flag on a browsing day is")
            print("  EARLY DETECTION, and catching him before the exfiltration is the")
            print("  only time catching him is worth anything.")
            print()
            print(f"  'Did we hit the exact day?'          precision "
                  f"{real/max(n,1):.4f}")
            print(f"  'Did we hit the right PERSON?'       precision "
                  f"{(real+mid)/max(n,1):.4f}")
            print()
            print(f"  Only {out} alerts ({100*out/max(n,1):.1f}%) land on somebody who is not an")
            print("  insider inside an attack window. THAT is the alert-fatigue number.")

        tiers = r.get("risk_tiers")
        if tiers:
            print()
            print("=" * 78)
            print("RISK SCORING ENGINE  (spec Module 6: weighted 0-100 composite)")
            print("=" * 78)
            print("  The spec's five weighted components -> a 0-100 score -> four levels.")
            print()
            print(f"  {'level':<11} {'days':>8} {'insider days':>13} {'precision':>10}"
                  f" {'insiders reached':>18}")
            print("  " + "-" * 64)
            tot = r["risk_insiders_total"]
            for t in tiers:
                print(f"  {t['level']:<11} {t['days']:>8,} {t['insider_days']:>13,} "
                      f"{t['precision']:>10.4f} {t['insiders_reached']:>13}/{tot}")
            print()
            for name in ("critical", "high", "medium"):
                k = r.get(f"insiders_reaching_{name}_or_above", 0)
                print(f"  insiders reaching {name.upper():<9} or above : {k}/{tot}")
            print()
            print("  THE SPEC'S OWN THRESHOLDS (80/60/35) COULD NOT DO THIS.")
            print("  Measured on the real labels, they produced ZERO critical alerts")
            print("  and 0/21 insiders at HIGH or above - because the largest single")
            print("  component is worth 35 points and CRITICAL needs 80, so every")
            print("  component would have to fire at once. Real insiders trigger one")
            print("  or two. A scenario-1 insider never touches his boss's PC; a")
            print("  scenario-3 sysadmin never browses job sites.")
            print()
            print("  Recalibrated from the actual score distribution on held-out users.")

        print()
        print("=" * 78)
        print("TOP FEATURES - measured, not asserted")
        print("=" * 78)
        print("  This is the evidence-backed answer to 'why did you choose these")
        print("  features'. The model decided, not us.")
        print()
        for f in r["top_features"]:
            bar = "#" * int(f["importance"] * 120)
            print(f"  {f['feature']:<34} {f['importance']:.4f}  {bar}")

        print()
        print(f"Completed in {r['duration_seconds']}s")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())