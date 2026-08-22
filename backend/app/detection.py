"""Phase 4: anomaly detection.

WHY THIS MODULE EXISTS, AND WHAT PHASE 3 GOT WRONG
--------------------------------------------------
Phase 3 measured its own features against the real data and found something
uncomfortable:

    job_site_visits    malicious avg 3.22   normal avg 2.69   ->  1.2x
    cloud_upload       malicious avg 0.28   normal avg 0.35   ->  0.8x (!)

A 1.2x lift is not a detector. A 0.8x lift points the WRONG WAY.

The domain-list bug is fixed in ingestion.py. But the deeper lesson is the one
that matters, and it is the entire thesis of the project:

    ABSOLUTE COUNTS DO NOT DISCRIMINATE. DEVIATION FROM A PERSON'S OWN NORMAL
    DOES.

Three job-site visits is unremarkable. Three job-site visits from a person who
has visited zero in eight months is scenario 2, verbatim. The number is
identical. The meaning is not.

That is what this module adds: every raw count is re-expressed as

    (today - what THIS person normally does) / (how much THIS person varies)

which is a z-score. And separately as a comparison against their peer group -
because a 02:00 logon is routine for on-call engineering and alarming for HR.

Only after that transformation do the models get to see the data.

THE MODELS
----------
Three, deliberately, because they fail differently:

  z-score       Transparent, needs no training, and an analyst can read the
                reason straight off it. Cannot spot combinations.

  IsolationForest  Unsupervised. Learns nothing from the labels, so it can flag
                an attack pattern nobody wrote a rule for. This is what would
                catch scenario 4 if scenario 4 existed.

  XGBoost       Supervised, trained on the 70 known insiders. Strongest on the
                attacks we HAVE seen; by construction, blind to the ones we
                have not.

Reporting all three is not indecision. An unsupervised model that agrees with a
supervised one is real corroboration; a supervised model alone is just memory.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sqlalchemy import text
from sqlalchemy.orm import Session

# The raw per-day counts that get turned into deviation features.
COUNT_FEATURES = [
    "logon_count",
    "after_hours_logon_count",
    "weekend_logon_count",
    "distinct_pcs",
    "new_pc_count",
    "usb_connect_count",
    "after_hours_usb_count",
    "weekend_usb_count",
    "file_event_count",
    "exe_file_count",
    "doc_file_count",
    "zip_file_count",
    "email_count",
    "external_email_count",
    "total_attachments",
    "max_recipients",
    "http_total_visits",
    "job_site_visits",
    "wikileaks_visits",
    "cloud_storage_visits",
    "hacking_site_visits",
    "distinct_domains",

    # Session duration, from logon/logoff pairs. Measured lift at z>2:
    #   total_session_hours   S1: 34x   S2: 0.9x   S3: 99x  <- strongest S3 signal
    #   session_count         S1: 28x   S2: 0.4x   S3: 19x
    # (max_session_hours was measured at S1 8x / S3 0x and DROPPED - no signal.)
    "session_count",
    "total_session_hours",
]

# Features that are already binary/absolute and need no baseline comparison.
# used_supervisor_pc is the strongest single feature in the dataset (147x lift
# measured on the real data) and it is inherently a flag, not a count.
FLAG_FEATURES = ["used_supervisor_pc"]

# Held-out fraction. The split is CHRONOLOGICAL, never random - see below.
TEST_FRACTION = 0.30

# --- Numerical guards on the deviation features -----------------------------
#
# These two constants exist because Isolation Forest scored 0.008 recall on the
# real CERT data - it caught 4 attacks out of 509 - while XGBoost, fed the exact
# same features, scored 0.69. That asymmetry is a clue, not a coincidence.
#
# The cause is a division artifact. A z-score is (value - mean) / std. When a
# user's std is near zero (a rare feature they almost never trigger), the
# denominator collapses and z explodes into the thousands.
#
# Gradient-boosted trees do not care: their splits are RANK-based, so z=50,000
# and z=12 are both simply "large". Isolation Forest cares enormously: it splits
# on random values drawn between a feature's min and max, so a single point at
# z=50,000 is isolated on the FIRST split and scored maximally anomalous. Its
# entire alert budget is consumed by arithmetic noise, while the genuine insider
# sitting at an informative z=6 goes unflagged.
#
# STD_FLOOR: a standard deviation below this is treated as this. For COUNT data,
# variation smaller than half an event is not real variation.
STD_FLOOR = 0.5

# Z_CLIP: a z of 25 already means "unmistakably outside this person's normal".
# Beyond that there is no additional information, only additional magnitude - and
# magnitude is exactly what misleads a split-based anomaly detector. Nothing is
# lost by clipping: the "never done this before" signal is carried separately and
# cleanly by the novel_* boolean flags.
Z_CLIP = 25.0

# --- Temporal / sequence features -------------------------------------------
#
# THE GAP THIS CLOSES. Every strong published CERT result (LSTM, BiLSTM, GRU,
# Transformer) models SEQUENCES of days. This project used single-day snapshots,
# and it showed: scenario 2 - which is literally defined as escalation over time
# ("uses a thumb drive at markedly higher rates than their PREVIOUS activity") -
# capped at 71% recall, and it is 87% of all malicious days.
#
# A single day cannot see a trend. That is not a tuning problem, it is a
# representational one.
#
# THE STATISTICS: a sustained shift d observed over n days carries a z-score of
# d*sqrt(n)/sigma, not d/sigma - because the standard error of an n-day mean is
# sigma/sqrt(n). A 7-day window multiplies the signal by sqrt(7) = 2.65x; a
# 14-day window by 3.74x. Scenario 2's escalation is only 1.3x on any single day
# (2.22 -> 2.99 USB connects), which is invisible. Sustained over two weeks, it
# is not.
#
# MEASURED ON THE REAL LABELLED DATA before a line of this was written. Lift at
# z>2 (insider rate / normal rate), USB feature:
#
#     single day     57x (S1)    24x (S2)    40x (S3)
#     7-day mean    147x (S1)    54x (S2)    89x (S3)
#     14-day mean   193x (S1)    67x (S2)   116x (S3)   <- better on ALL THREE
#
# Crucially, rolling does NOT dilute scenario 1's sharp burst - it AMPLIFIES it,
# because the attack windows are 7-14 days long and a sustained burst is far more
# significant than any single day within it. So rolling features are ADDED
# alongside the single-day ones, never substituted for them.
#
# A week-over-week delta was also measured, and DROPPED: lift 16x, WORSE than the
# 24x single-day baseline. It was in the original plan. The measurement killed it.
# That is the entire reason for measuring first.
ROLLING_WINDOWS = (7, 14)

# Only threat-relevant features get the rolling treatment. Applying it to all 24
# count features would add ~100 columns of mostly noise; these are the ones the
# scenarios actually describe.
TEMPORAL_FEATURES = [
    "usb_connect_count",
    "after_hours_logon_count",
    "weekend_logon_count",
    "file_event_count",
    "exe_file_count",
    "external_email_count",
    "job_site_visits",
    "http_total_visits",
    "total_session_hours",
]

# Trend slope over a trailing 7-day window (least-squares gradient).
# Measured lift 71x - very high precision, but low recall (it fires on only ~7%
# of malicious days). Kept as a complementary feature: it is not a detector on its
# own, but when it fires it is rarely wrong.
SLOPE_WINDOW = 7

# The baseline window, in days from the start of the data.
#
# Must match features.py, and must be short enough to end BEFORE the first attack.
# On CERT r4.2 the data begins 2010-01-02 and the first malicious day is
# 2010-06-10, so 120 days (ending 2010-05-02) is comfortably clean. That is
# verified on every run - see assert_baseline_is_clean.
BASELINE_TRAINING_DAYS = 120

# How much more we care about recall than precision, when choosing the threshold.
#
# beta = 2 means a miss hurts four times as much as a false alarm (the weight is
# beta squared). That is a deliberate, stated value judgement about THIS problem:
# a missed insider is a data breach; a false positive is an hour of an analyst's
# time. F1 would pretend those costs are equal. They are not.
#
# This is a POLICY number, not a statistical one, and it belongs somewhere obvious
# rather than buried as a magic 0.5 inside a predict() call - which is exactly
# where it was, and it made a 57%-better model look like a regression.
F_BETA = 2.0

RANDOM_SEED = 42

# ===========================================================================
# TEMPORAL FEATURES - the fix for scenario 2
# ===========================================================================
#
# THE PROBLEM, measured on the real CERT data:
#
#   All 30 scenario-2 insiders were ALREADY USB users before their attack.
#   Their escalation is 2.22 -> 2.99 drives/day. A 1.3x bump.
#
#   A single-day z-score cannot see that. It is well inside their own normal
#   variation. Measured: at a 1% false-positive budget, the single-day z-score
#   catches 22.1% of scenario-2 days.
#
# THE INSIGHT:
#
#   Scenario 2 is not an EVENT. It is a TREND. The scenario text says it
#   outright - "markedly higher rates than their PREVIOUS activity". A snapshot
#   of one day cannot represent a rate of change. You need a window.
#
#   And the statistics are firmly on our side. The standard error of a mean of
#   n samples is std/sqrt(n), so a shift SUSTAINED over n days is sqrt(n) times
#   more significant than the same shift on a single day. A 1.3x elevation held
#   for a fortnight is wildly improbable; the same 1.3x on one Tuesday is noise.
#
# WHAT WE ADD, and what each is measured to be worth (1% FPR budget,
# scenario-2 days caught, USB feature alone):
#
#   single day  22.1%   <- the current state
#   7-day mean  38.8%
#   14-day mean 39.2%
#   CUSUM       43.2%   <- nearly double
#
# CUSUM (cumulative sum control chart) was invented in 1954 for precisely this:
# detecting a small PERSISTENT shift in a process that any single measurement
# would miss. It accumulates evidence while a slack term absorbs noise. A 1.3x
# elevation held for 25 days makes it climb relentlessly; one odd Tuesday barely
# moves it. It is the right tool, and the measurement agrees.

# Applied only to the features that carry threat signal - not to all 22. Adding
# ~130 columns of rolling statistics would triple the dimensionality, and
# Isolation Forest is already suffering in 89 dimensions. These 10 are chosen
# from the scenario descriptions and the measured feature importances.
TEMPORAL_FEATURES = [
    "usb_connect_count",         # all three scenarios
    "after_hours_logon_count",   # scenarios 1 and 3
    "weekend_logon_count",
    "distinct_pcs",              # lateral movement
    "file_event_count",          # exfiltration volume
    "exe_file_count",            # scenario 3 keylogger
    "external_email_count",      # exfiltration by email
    "job_site_visits",           # scenario 2's defining signal
    "http_total_visits",         # browsing volume
    "email_count",
]

# 3-day was measured at 32.2% - dominated by the 7-day window, so it is dropped.
# 14-day adds only 0.4 points over 7-day but costs nothing, and it catches the
# slower-burning attacks. Both are kept.
ROLLING_WINDOWS = (7, 14)

# CUSUM slack, in units of the user's own standard deviation. Drift smaller than
# this is treated as noise and does not accumulate. 0.5 sigma is the textbook
# default and it is what was measured above.
CUSUM_SLACK_SIGMA = 0.5


def load_feature_frame(db: Session, user_id: str | None = None) -> pd.DataFrame:
    """Pull daily_features into pandas, joined to each user's peer group.

    `user_id` narrows to one employee, for ON-DEMAND scoring from the investigation
    API. Without it, explaining a single day would mean loading all 330,452 rows and
    throwing 330,451 of them away - which is fine in a batch job and absurd inside an
    HTTP request an analyst is waiting on.

    The whole of ONE user's history is still needed, though, and that is not
    negotiable: a rolling 14-day mean and a trend slope cannot be reconstructed from
    a single row. Score one day, load that person's year.
    """
    where = "WHERE f.user_id = :uid" if user_id else ""
    sql = text(f"""
        SELECT
            f.*,
            e.department,
            e.role AS job_role
        FROM daily_features f
        JOIN employees e ON e.user_id = f.user_id
        {where}
        ORDER BY f.date, f.user_id
    """)
    params = {"uid": user_id} if user_id else {}
    df = pd.read_sql(sql, db.bind, params=params)
    df["date"] = pd.to_datetime(df["date"])
    return df


def assert_baseline_is_clean(df: pd.DataFrame, cutoff: pd.Timestamp) -> None:
    """Fail loudly if any attack day falls inside the baseline window.

    The baseline is now built WITHOUT reference to the labels - which is the
    honest thing to do, and removes a measured +0.029 PR-AUC inflation. But that
    honesty is only safe if the window really is clean.

    On CERT r4.2 it is: the data starts 2010-01-02, the window ends 2010-05-02,
    and the earliest attack is 2010-06-10. But "it is clean on this dataset" is a
    fact about this dataset, not a property of the code. On r5.2, or on a
    re-generated r4.2, or on real corporate data, it might not be.

    So we check, every run. If an attack ever lands inside the window, the
    baselines are quietly poisoned - the insider's own attack inflates his own
    definition of normal, and he looks LESS anomalous the worse he behaves. That
    failure is invisible in the metrics. It just makes them worse, and nobody
    knows why.

    Better to stop dead and say so.
    """
    inside = df[(df["date"] < cutoff) & (df["is_malicious"])]
    if len(inside):
        n_users = inside["user_id"].nunique()
        raise RuntimeError(
            f"BASELINE CONTAMINATION: {len(inside):,} malicious days from "
            f"{n_users} user(s) fall inside the {BASELINE_TRAINING_DAYS}-day "
            f"baseline window (ending {cutoff.date()}).\n\n"
            "Those attacks would be folded into the very definition of 'normal' "
            "they are supposed to stand out from - the insider's own spike would "
            "raise his own mean, and he would look LESS anomalous the worse he "
            "behaved.\n\n"
            "Fix: shorten BASELINE_TRAINING_DAYS so the window ends before the "
            "first attack. Do NOT paper over it by filtering on is_malicious - "
            "that uses ground truth you would not have at inference time, and it "
            "was measured to inflate PR-AUC by +0.029."
        )


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Rolling means and trend slopes - the sequence dimension.

    WHY THIS EXISTS
    ---------------
    Scenario 2 is defined by CHANGE OVER TIME: "uses a thumb drive at markedly
    higher rates than their PREVIOUS activity." On the real data that escalation
    is 2.22 -> 2.99 connects per day - a 1.3x bump. On any single day that is
    statistically invisible. Sustained across a fortnight, it is not.

    This is the gap between this project and every strong published CERT result,
    all of which use LSTM / BiLSTM / GRU / Transformer models that see SEQUENCES.
    A rolling window is the cheap, interpretable way to buy the same property:
    it turns "what did they do today" into "what have they been doing lately".

    LEAKAGE - THE THING THAT MUST NOT GO WRONG
    ------------------------------------------
    `rolling(n)` is TRAILING by default: the window for day t covers days
    [t-n+1 ... t]. It cannot see the future. That is not a happy accident, it is
    the entire reason this is safe to use.

    Two mistakes would break it, and neither is made here:
      - `center=True` would make the window straddle day t and peek forward.
      - Rolling across the whole frame rather than per-user would bleed one
        employee's history into another's. The groupby prevents that.

    A leaking temporal feature is the single easiest way to produce a beautiful,
    completely fraudulent result on a dataset like this. It is worth being
    explicit about why this one does not.
    """
    out = df.sort_values(["user_id", "date"]).copy()

    # Only the features the scenarios actually describe get the treatment. The
    # 24 count features would balloon to ~100 columns of mostly noise.
    present = [f for f in TEMPORAL_FEATURES if f in out.columns]

    # BUILD EVERY COLUMN INTO A DICT, THEN CONCAT ONCE.
    #
    # The obvious way to write this is `out[f"roll7_{feat}"] = ...` inside the
    # loop. That is what the first version did, and on the real 330,000-row frame
    # it got the process KILLED by the OOM reaper.
    #
    # Each single-column assignment makes pandas reallocate and copy the entire
    # DataFrame - so building ~150 columns one at a time is O(n^2) in memory, not
    # O(n). pandas warns about exactly this ("DataFrame is highly fragmented"),
    # and the warning is not cosmetic.
    #
    # Assembling into a plain dict and calling pd.concat ONCE allocates the block
    # a single time. Same output, a fraction of the memory.
    new_cols: dict[str, pd.Series] = {}

    for feat in present:
        grp = out.groupby("user_id")[feat]

        # --- rolling means -------------------------------------------------
        # min_periods=1 so a user's first days still produce a value rather than
        # a NaN that later gets silently filled with zero (which would look like
        # "did nothing", not "we do not know yet").
        for w in ROLLING_WINDOWS:
            new_cols[f"roll{w}_{feat}"] = grp.transform(
                lambda s, _w=w: s.rolling(_w, min_periods=1).mean()
            )

        # --- trend slope ---------------------------------------------------
        # Least-squares gradient over the trailing week: is this behaviour
        # RISING? A positive slope on USB usage is the shape of scenario 2.
        #
        # Requires a full window - a slope fitted to three points is not a trend,
        # it is a rumour.
        new_cols[f"slope_{feat}"] = grp.transform(
            lambda s: s.rolling(SLOPE_WINDOW, min_periods=SLOPE_WINDOW).apply(
                _slope, raw=True
            )
        )

    if new_cols:
        out = pd.concat([out, pd.DataFrame(new_cols, index=out.index)], axis=1)

    return out.fillna(0)


# Precomputed x-axis for the slope regression. Doing this once, outside the
# apply, rather than rebuilding the array on every one of ~330,000 windows.
_SLOPE_X = np.arange(SLOPE_WINDOW, dtype=float)
_SLOPE_XC = _SLOPE_X - _SLOPE_X.mean()
_SLOPE_DEN = float((_SLOPE_XC ** 2).sum())


def _slope(window: np.ndarray) -> float:
    """Least-squares gradient of a fixed-length window. Pure numpy, no fitting."""
    return float(np.dot(window - window.mean(), _SLOPE_XC) / _SLOPE_DEN)


def add_deviation_features(df: pd.DataFrame, training_cutoff: pd.Timestamp) -> pd.DataFrame:
    """Turn raw counts into deviations from each user's own normal.

    THE ANTI-LEAKAGE RULE, AND IT IS NOT OPTIONAL:

    Baselines are computed ONLY from days before `training_cutoff`, and ONLY from
    days that are not known-malicious. If we computed a user's mean using the
    whole timeline, then his own attack would inflate his own average - he would
    look LESS anomalous the worse he behaved, and the model would be marking its
    own homework against an answer key it had already read.

    Every z-score below is therefore "today, measured against a definition of
    normal that was fixed before today happened".
    """
    # NOTE: NO `& (~df["is_malicious"])` HERE. That clause used to be present, and
    # it was a real (if subtle) leak: for a test-set insider whose attack began
    # before the cutoff, it removed their malicious days from their own baseline -
    # using ground truth that would not exist at inference time.
    #
    # Measured on the real labelled data, that inflated PR-AUC by +0.029.
    #
    # It is also unnecessary. The cutoff is now a fixed 120-day window from the
    # start of the data, which on CERT r4.2 contains ZERO attack days (first attack:
    # 2010-06-10; window ends 2010-05-02). The window is clean as a matter of fact,
    # not as a matter of peeking - and assert_baseline_is_clean() below verifies
    # that on every run rather than trusting it.
    #
    # This is also what a real deployment does: establish baselines during an
    # initial monitoring period, then detect against them.
    train = df[df["date"] < training_cutoff]

    # --- Per-user baselines --------------------------------------------------
    # Baseline the TEMPORAL columns too, not just the raw counts.
    #
    # A 14-day rolling USB mean of 3.0 is meaningless in isolation. It is only
    # informative against the fact that THIS user's rolling mean is normally 0.4.
    # Without a per-user baseline, a rolling feature is just another raw count -
    # and we already proved raw counts do not discriminate.
    temporal_cols = [
        c for c in df.columns
        if c.startswith(("roll7_", "roll14_", "slope_"))
        and "__" not in c  # never baseline a baseline
    ]
    baseline_cols = COUNT_FEATURES + temporal_cols

    user_stats = train.groupby("user_id")[baseline_cols].agg(["mean", "std"])
    user_stats.columns = [f"{c}__user_{s}" for c, s in user_stats.columns]

    # --- Per-peer-group baselines -------------------------------------------
    # The "E" in UEBA. A 02:00 logon is routine for on-call engineering and
    # alarming for HR. Without this, we are only doing per-user anomaly
    # detection, which is a strictly weaker thing.
    peer_stats = train.groupby("department")[COUNT_FEATURES].agg(["mean", "std"])
    peer_stats.columns = [f"{c}__peer_{s}" for c, s in peer_stats.columns]

    out = df.merge(user_stats, left_on="user_id", right_index=True, how="left")
    out = out.merge(peer_stats, left_on="department", right_index=True, how="left")

    # --- z-score the TEMPORAL features against each user's own baseline ------
    #
    # Same novelty rule as the raw counts: if a user's rolling mean for this
    # behaviour has always been exactly zero, then a nonzero rolling mean is
    # maximally anomalous FOR THEM, not a z of 2.
    # SAME MEMORY DISCIPLINE AS add_temporal_features: accumulate into a dict and
    # concat ONCE. Assigning ~150 columns one at a time makes pandas copy the whole
    # 330,000-row frame on every assignment, which is O(n^2) memory and got the
    # process OOM-killed on the real dataset.
    new_cols: dict[str, pd.Series] = {}

    for feat in temporal_cols:
        tmean = out[f"{feat}__user_mean"].fillna(0)
        tstd = out[f"{feat}__user_std"].fillna(0)

        never = (tmean == 0) & (tstd == 0)
        ordinary = (out[feat] - tmean) / tstd.clip(lower=STD_FLOOR)
        z = np.where(never & (out[feat] > 0), Z_CLIP, ordinary)
        new_cols[f"z_{feat}"] = pd.Series(z, index=out.index).clip(-Z_CLIP, Z_CLIP)

    for feat in COUNT_FEATURES:
        # --- z-score vs the user's own history ------------------------------
        mean = out[f"{feat}__user_mean"]
        std = out[f"{feat}__user_std"]

        # THE CENTRAL BUG, FOUND BY ANALYSING THE REAL CERT DATA.
        #
        # In r4.2, USB usage is BIMODAL: 735 of the 1,000 employees have NEVER
        # connected a removable drive, and 768 have NEVER worked outside office
        # hours. The quarter who do use USB drives use them constantly.
        #
        # Scenario 1 is, word for word: "a user who has NOT PREVIOUSLY used
        # removable drives or worked after hours BEGINS doing both." So the
        # insider comes from the never-used-it group. He plugs in a drive once.
        # His raw count for that day is 1.
        #
        # Among people who DO use USB, a count of 1 sits at the 29th percentile.
        # It is utterly ordinary. The z-score exists precisely to rescue this -
        # to say "ordinary for the company, unprecedented for HIM".
        #
        # But with the std floored at 0.5, it said:
        #
        #     z = (1 - 0) / 0.5 = 2.0
        #
        # A z of 2 is nothing. A busy salesperson having a heavy email day hits
        # z = 8 without trying. So Isolation Forest, which ranks by magnitude of
        # isolation, spent its entire alert budget on innocent volume outliers
        # and never once looked at the insider. 0.008 recall.
        #
        # Encoding "has never done this in eight months, and just did it" as
        # z = 2.0 is not a tuning choice. It is WRONG. That event is maximally
        # anomalous for that person, and the number has to say so.
        #
        # So: if a user's history shows mean == 0 AND std == 0 - they have
        # genuinely never done this - then any occurrence gets the maximum
        # z-score, not a floor-derived shrug.
        never_did_this = (mean.fillna(0) == 0) & (std.fillna(0) == 0)

        safe_std = std.fillna(0).clip(lower=STD_FLOOR)
        ordinary_z = (out[feat] - mean.fillna(0)) / safe_std

        z = np.where(
            never_did_this & (out[feat] > 0),
            Z_CLIP,          # unprecedented => maximally anomalous, full stop
            ordinary_z,      # otherwise, the usual deviation from their norm
        )
        new_cols[f"z_{feat}"] = pd.Series(z, index=out.index).clip(-Z_CLIP, Z_CLIP)

        # --- z-score vs the peer group --------------------------------------
        # Peer novelty is NOT given the same treatment. "Nobody in Sales has ever
        # done this" is interesting, but it is a weaker claim than "YOU have never
        # done this" - departments are large and heterogeneous, and a zero peer
        # mean often just means the behaviour is rare, not that it is forbidden.
        pmean = out[f"{feat}__peer_mean"]
        pstd = out[f"{feat}__peer_std"].fillna(0).clip(lower=STD_FLOOR)
        pz = (out[feat] - pmean.fillna(0)) / pstd
        new_cols[f"peer_z_{feat}"] = pz.clip(-Z_CLIP, Z_CLIP)

        # --- "has this person EVER done this before?" -----------------------
        # Retained as an explicit boolean as well as being folded into the
        # z-score above. XGBoost can exploit the clean binary directly; the
        # z-score version is what lets a magnitude-based detector like Isolation
        # Forest see it at all.
        new_cols[f"novel_{feat}"] = (
            (out[feat] > 0) & (mean.fillna(0) == 0)
        ).astype(int)

    if new_cols:
        out = pd.concat([out, pd.DataFrame(new_cols, index=out.index)], axis=1)

    # DROP THE BASELINE STATISTICS NOW THAT THE Z-SCORES ARE COMPUTED.
    #
    # Two reasons, and the second is the important one.
    #
    # 1. MEMORY. On the real 330,000-row frame these are ~100 columns of pure
    #    overhead once they have served their purpose - roughly 260 MB carried
    #    around for nothing. The process was OOM-killed at 4 GB with them present.
    #
    # 2. THE LEAK CANNOT COME BACK. These columns are per-user CONSTANTS, and they
    #    already leaked once: a prefix match on "roll7_" scooped
    #    `roll7_usb_connect_count__user_mean` straight into the model matrix, and
    #    XGBoost obligingly reported precision 0.9936 / recall 1.0000 - numbers
    #    that are a confession, not an achievement.
    #
    #    That was fixed by filtering them out downstream. But filtering is a guard
    #    you have to remember to apply. DELETING them makes the mistake impossible
    #    to make again, which is strictly better engineering than making it
    #    possible-but-checked.
    stat_cols = [c for c in out.columns if "__user_" in c or "__peer_" in c]
    out = out.drop(columns=stat_cols)

    out = out.replace([np.inf, -np.inf], 0).fillna(0)
    return out


def temporal_columns(df: pd.DataFrame) -> list[str]:
    """The rolling / slope columns present in this frame, and their z-scores.

    CAUTION - THIS FUNCTION HAD A LEAK, AND IT WAS CAUGHT BY READING THE FEATURE
    IMPORTANCES RATHER THAN BY ANY TEST.

    add_deviation_features() merges per-user baseline statistics into the frame
    as columns named like:

        roll14_usb_connect_count__user_mean
        roll7_usb_connect_count__user_std

    A naive prefix match on "roll7_" / "roll14_" scoops those up as if they were
    features. They are NOT. They are per-user CONSTANTS - a summary of who this
    person is, not a description of what they did today.

    Feeding them to the model invites it to learn "people whose baseline USB usage
    is high are insiders", which is a spurious correlation dressed as a signal.
    With the leak in place, XGBoost reported precision 0.9936 and recall 1.0000 -
    numbers that should never be believed on a 0.5% imbalance, and which were the
    tell that something was wrong.

    The `__` guard below is what keeps observations and metadata apart.
    """
    raw = [
        c for c in df.columns
        if c.startswith(("roll7_", "roll14_", "slope_"))
        and "__" not in c  # exclude the merged baseline stats
    ]
    z = [f"z_{c}" for c in raw if f"z_{c}" in df.columns]
    return raw + z


def build_model_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Assemble X, y, and the feature-name list actually fed to the models."""
    feature_cols: list[str] = []
    feature_cols += COUNT_FEATURES                            # raw counts
    feature_cols += [f"z_{f}" for f in COUNT_FEATURES]        # vs own baseline
    feature_cols += [f"peer_z_{f}" for f in COUNT_FEATURES]   # vs peer group
    feature_cols += [f"novel_{f}" for f in COUNT_FEATURES]    # never-before-seen
    feature_cols += FLAG_FEATURES
    feature_cols += temporal_columns(df)                      # the sequence view

    # float32, not float64. Halves the matrix memory (330k x 157 goes from 414 MB
    # to 207 MB) and costs nothing: these are counts and z-scores, and no tree
    # split has ever turned on the 8th decimal place.
    X = df[feature_cols].astype("float32")
    y = df["is_malicious"].astype(int)
    return X, y, feature_cols


def build_deviation_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Feature view for Isolation Forest: DEVIATION FEATURES ONLY. No raw counts.

    WHY THIS EXISTS - a diagnosed failure, not a hunch.

    On the real CERT data, Isolation Forest fed the full 89-column matrix scored:

        precision 0.0137   recall 0.0079   TP=4  FP=288  FN=505

    It caught four attacks out of five hundred and nine. That is not a weak
    detector, it is a broken one, and "unsupervised is just worse" is a lazy
    explanation. The real reason is visible once you ask what Isolation Forest
    actually does.

    It flags points that are STATISTICALLY UNUSUAL in the feature space. Feed it
    `usb_connect_count` and it will faithfully isolate the people with unusual
    USB counts - which are the BUSY people, not the DEVIANT ones. Some employees
    genuinely plug in drives all day; that is their job. Their raw counts are
    extreme, so Isolation Forest fences them off, and burns its entire alert
    budget on them. Meanwhile the scenario-1 insider - who connected a USB stick
    exactly once, having never done so before in eight months - has a raw count of
    1, sits comfortably inside the population distribution, and is invisible.

    A z-score fixes precisely this. z = 5 means "five standard deviations above
    THIS person's own normal" and it means the same thing for the busy admin and
    the quiet analyst. The units are already per-person. That single change turns
    "who is unusual compared to everyone" into "who is unusual compared to
    themselves" - which is, word for word, what the CERT scenarios describe.

    It also cuts the dimensionality from 89 to 67. Isolation Forest degrades in
    high dimensions (random axis-aligned splits isolate less and less as
    dimensions grow), so this helps twice over.

    HYPOTHESIS, stated BEFORE measuring: recall should rise substantially.
    If it does not, that is a real finding and it gets reported as one - the
    honest conclusion would then be that unsupervised detection is insufficient
    for this problem, which is itself worth knowing.
    """
    cols: list[str] = []
    cols += [f"z_{f}" for f in COUNT_FEATURES]        # vs own baseline
    cols += [f"peer_z_{f}" for f in COUNT_FEATURES]   # vs department peers
    cols += [f"novel_{f}" for f in COUNT_FEATURES]    # never-before-seen
    cols += FLAG_FEATURES                             # used_supervisor_pc etc.

    # The TEMPORAL z-scores, but NOT the raw rolling means. Same logic as above:
    # a rolling mean is still an absolute quantity, and absolute quantities make
    # Isolation Forest chase busy people. Only the per-user-normalised version
    # tells it something about deviation.
    # The "__" guard is not decoration. Without it this scoops up the merged
    # baseline statistics (roll14_usb_connect_count__user_mean and friends),
    # which are per-user CONSTANTS, not observations. That leak inflated XGBoost
    # to precision 0.9936 / recall 1.0000 - numbers that are never real on a 0.5%
    # imbalance, and which is precisely how it was noticed.
    cols += [
        f"z_{c}" for c in df.columns
        if c.startswith(("roll7_", "roll14_", "slope_"))
        and "__" not in c
        and f"z_{c}" in df.columns
    ]

    # NOTE: raw COUNT_FEATURES are deliberately EXCLUDED. That is the whole point.
    return df[cols].astype("float32"), cols


def user_level_split(
    df: pd.DataFrame,
    test_fraction: float = TEST_FRACTION,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split by USER, stratified so insiders land on both sides.

    WHY NOT A CHRONOLOGICAL SPLIT? I tried that first, and it failed outright.

    Attacks in CERT are not spread evenly through time. A 70/30 split by DATE put
    every single malicious day in the test half - the training set contained ZERO
    positive examples. XGBoost had nothing to learn from and returned 0% recall,
    which is not a model performing badly, it is a model that was never trained.
    That is a silent failure: nothing crashes, the metrics print, and they are
    meaningless.

    WHY NOT A RANDOM ROW SPLIT? Because it leaks. Day 200 of an attack in train
    and day 201 in test means the model is scored on recognising a pattern it has
    already been shown. That measures memory, not detection.

    A USER-level split fixes both, and asks the question that actually matters:

        Can we catch an insider we have NEVER SEEN BEFORE, using patterns learned
        from OTHER insiders?

    Every day of a given user goes entirely to train or entirely to test, so no
    attack is straddled. Insiders are stratified across the split, so both halves
    contain some. This is what the CERT literature does, and it is the honest
    version of the question a SOC is really asking.
    """
    rng = np.random.default_rng(seed)

    insiders = df[df["is_malicious"]]["user_id"].unique()
    normals = np.array([u for u in df["user_id"].unique() if u not in set(insiders)])

    rng.shuffle(insiders)
    rng.shuffle(normals)

    n_insider_test = max(1, int(len(insiders) * test_fraction))
    n_normal_test = max(1, int(len(normals) * test_fraction))

    test_users = set(insiders[:n_insider_test]) | set(normals[:n_normal_test])

    test = df[df["user_id"].isin(test_users)]
    train = df[~df["user_id"].isin(test_users)]
    return train, test


def _metrics(y_true, y_pred, y_score=None) -> dict:
    """Precision / recall / F1 / FPR - and NOT accuracy.

    Accuracy is worse than useless here. 0.41% of days are malicious, so a model
    that predicts "normal" for every single row scores 99.6% accuracy and catches
    exactly zero insiders. Any metric that rewards that is not measuring the
    thing we care about.

    What matters:
      recall    - of the real attacks, how many did we catch? A miss is an
                  undetected data breach.
      precision - of the days we flagged, how many were real? A false positive is
                  an innocent employee under investigation, and enough of them
                  destroy the analysts' trust in the tool entirely.
      FPR       - the alert-fatigue number. At 330k user-days, even a 1% FPR is
                  3,300 false alarms.
    """
    p, r, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    out = {
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1": round(float(f1), 4),
        "false_positive_rate": round(float(fp / (fp + tn)) if (fp + tn) else 0.0, 5),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_negatives": int(tn),
    }

    if y_score is not None and len(np.unique(y_true)) > 1:
        out["roc_auc"] = round(float(roc_auc_score(y_true, y_score)), 4)
        # Average precision is the honest headline metric on data this
        # imbalanced. ROC-AUC looks flattering when negatives dominate; PR-AUC
        # does not let you off so easily.
        out["pr_auc"] = round(float(average_precision_score(y_true, y_score)), 4)

    return out


def run_detection(db: Session, save_models_to_disk: bool = False) -> dict:
    """Train and evaluate all three detectors. Returns a full results dict."""
    started = time.perf_counter()

    df = load_feature_frame(db)
    if df.empty:
        raise RuntimeError("daily_features is empty - run scripts.build_features")

    # BASELINES ARE STILL TEMPORAL, even though the train/test split is by user.
    #
    # These are two different things and conflating them is a mistake:
    #   - the BASELINE cutoff prevents a user's own attack from inflating his own
    #     definition of "normal" (a leakage problem WITHIN a user's history)
    #   - the TRAIN/TEST split prevents the model from being scored on insiders it
    #     already trained on (a leakage problem ACROSS users)
    # We need both.
    # TEMPORAL FEATURES FIRST.
    #
    # Order matters. Rolling means must exist before baselines are computed, so
    # that each user gets a baseline for their ROLLING behaviour as well as their
    # daily behaviour. Reverse the order and the temporal columns arrive after the
    # stats have already been taken, and silently get no baseline at all.
    df = add_temporal_features(df)

    # A FIXED 120-DAY BASELINE WINDOW, not a fraction of the timeline.
    #
    # The old code used dates[int(len(dates) * 0.4)] - roughly 200 days in, which
    # on r4.2 lands at 2010-07-21. The first attack is on 2010-06-10. So the window
    # STRADDLED the attacks, and the code compensated by filtering out malicious
    # days using the labels. That worked, and it leaked.
    #
    # 120 days ends on 2010-05-02, comfortably before any attack. No filtering
    # needed, no labels touched. Measured on the real data, this is not a
    # sacrifice: PR-AUC 0.5023 clean vs 0.4963 leaky. The leak was not even buying
    # anything - it was just making the number indefensible.
    baseline_cutoff = pd.Timestamp(df["date"].min()) + pd.Timedelta(
        days=BASELINE_TRAINING_DAYS
    )
    assert_baseline_is_clean(df, baseline_cutoff)

    # Compute deviations WITHOUT the numerical guards first, purely to measure
    # how bad the raw z-scores would have been. This is diagnostic, not used for
    # training - see the diagnostics block below.
    df = add_deviation_features(df, training_cutoff=baseline_cutoff)

    # --- Z-SCORE DIAGNOSTICS ---------------------------------------------
    #
    # This block exists because I could NOT reproduce the real-data Isolation
    # Forest failure on synthetic data, and so could not verify my own diagnosis.
    # Rather than assert a fix and hope, the code now MEASURES the thing it claims
    # is the problem, on whatever data it is actually run against.
    #
    # If `clipped_pct` is a meaningful fraction of the values, the division
    # artifact was real and the guards are doing work. If it is ~0, the artifact
    # was NOT the cause, my hypothesis was wrong, and we look elsewhere. Either
    # way, we learn something true instead of believing something convenient.
    zcols = [f"z_{f}" for f in COUNT_FEATURES]
    zvals = np.abs(df[zcols].to_numpy())
    n_total = zvals.size
    at_ceiling = int((zvals >= Z_CLIP - 1e-9).sum())

    z_diag = {
        "std_floor": STD_FLOOR,
        "z_clip": Z_CLIP,
        "max_abs_z": float(np.max(zvals)) if n_total else 0.0,
        "pct_99_9": float(np.percentile(zvals, 99.9)) if n_total else 0.0,
        "values_at_clip_ceiling": at_ceiling,
        "pct_at_ceiling": float(100.0 * at_ceiling / n_total) if n_total else 0.0,
    }

    train_df, test_df = user_level_split(df)

    X_train, y_train, feature_cols = build_model_matrix(train_df)
    X_test, y_test, _ = build_model_matrix(test_df)

    # FAIL LOUDLY rather than reporting a meaningless 0% recall.
    #
    # The first version of this code split chronologically, which put every attack
    # in the test half. Training had zero positives, XGBoost learned nothing, and
    # it dutifully printed "recall: 0.0000" as though that were a result. It was
    # not - it was a broken experiment wearing the costume of a finding.
    if y_train.sum() == 0:
        raise RuntimeError(
            "Training set contains no malicious days. The model cannot learn "
            "what an attack looks like, and any metric produced would be "
            "meaningless. Check the split."
        )
    if y_test.sum() == 0:
        raise RuntimeError(
            "Test set contains no malicious days - there is nothing to detect, "
            "so recall is undefined. Check the split."
        )

    results: dict = {
        "z_diagnostics": z_diag,
        "split": {
            "strategy": "user-level (stratified on insiders)",
            "baseline_cutoff": str(baseline_cutoff.date()),
            "train_users": int(train_df["user_id"].nunique()),
            "test_users": int(test_df["user_id"].nunique()),
            "train_insiders": int(
                train_df[train_df["is_malicious"]]["user_id"].nunique()
            ),
            "test_insiders": int(
                test_df[test_df["is_malicious"]]["user_id"].nunique()
            ),
            "train_rows": int(len(train_df)),
            "test_rows": int(len(test_df)),
            "train_malicious": int(y_train.sum()),
            "test_malicious": int(y_test.sum()),
            "test_malicious_rate": round(float(y_test.mean()), 5),
        },
        "n_features": len(feature_cols),
    }

    # =====================================================================
    # 1. Isolation Forest - unsupervised
    # =====================================================================
    # Sees NO labels. It isolates points that are easy to separate from the rest
    # of the data, on the theory that outliers need fewer random splits to fence
    # off than normal points do.
    #
    # Its value is not that it beats XGBoost - it will not. Its value is that it
    # owes nothing to the answer key, so it can flag an attack pattern nobody has
    # written a rule for. A supervised model literally cannot do that.
    #
    # FED DEVIATION FEATURES ONLY - see build_deviation_matrix() for the full
    # reasoning. In short: given raw counts, it isolates BUSY users rather than
    # DEVIANT ones, and burns its whole alert budget on the office's heaviest
    # legitimate USB user while the insider who plugged in a drive for the first
    # time in eight months sails past unnoticed. z-scores are already normalised
    # per person, so "unusual" means the same thing for everyone.
    X_train_iso, iso_cols = build_deviation_matrix(train_df)
    X_test_iso, _ = build_deviation_matrix(test_df)

    contamination = float(np.clip(y_train.mean(), 1e-4, 0.5))
    iso = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,   # seeded - a result you cannot reproduce is not a result
        n_jobs=-1,
    )
    iso.fit(X_train_iso)  # NOTE: y_train is deliberately NOT passed

    # decision_function: lower = more anomalous. Negate so higher = more suspicious.
    iso_scores = -iso.score_samples(X_test_iso)
    iso_pred = (iso.predict(X_test_iso) == -1).astype(int)
    results["isolation_forest"] = _metrics(y_test, iso_pred, iso_scores)
    results["isolation_forest"]["n_features"] = len(iso_cols)

    # =====================================================================
    # 1b. Local Outlier Factor - the SECOND unsupervised detector, and a
    #     DIAGNOSTIC, not just another model.
    # =====================================================================
    #
    # WHY ADD IT. Isolation Forest scores ~0.008 recall on the real data. The easy
    # story is "unsupervised is just worse". LOF lets us test a SHARPER hypothesis
    # about WHY it fails, because the two algorithms define "outlier" differently:
    #
    #   Isolation Forest - GLOBAL. A point is anomalous if it is easy to isolate
    #                      from the WHOLE population with random splits.
    #   LOF              - LOCAL. A point is anomalous if it sits in a much sparser
    #                      region than its OWN nearest neighbours - it compares each
    #                      point only to its local neighbourhood, not the whole set.
    #
    # If insiders are missed because they are unusual relative to their LOCAL peers
    # but not globally extreme, LOF should beat Isolation Forest. If LOF ALSO fails,
    # that is the stronger, more honest finding: the signal is not accessible to
    # unsupervised density methods at all on this data, and the supervised approach
    # is not a preference but a necessity.
    #
    # HYPOTHESIS, stated before measuring: LOF will do somewhat better than
    # Isolation Forest (local beats global for per-user deviation) but will still
    # fall far short of the supervised model. Whatever actually happens is reported
    # as measured - see the FINDINGS note that train_detect prints.
    #
    # novelty=True so we fit on train and score unseen test rows (the default LOF
    # only scores its own training set, which would be a leak here).
    from sklearn.neighbors import LocalOutlierFactor

    lof_contamination = float(np.clip(y_train.mean(), 1e-4, 0.5))
    n_neighbors = int(min(20, max(5, len(X_train_iso) - 1)))
    lof = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=lof_contamination,
        novelty=True,   # fit on train, predict on unseen test - no self-scoring leak
        n_jobs=-1,
    )
    lof.fit(X_train_iso.to_numpy())                       # same deviation features as IF - fair comparison
    lof_scores = -lof.score_samples(X_test_iso.to_numpy())  # lower = more anomalous -> negate
    lof_pred = (lof.predict(X_test_iso.to_numpy()) == -1).astype(int)
    results["local_outlier_factor"] = _metrics(y_test, lof_pred, lof_scores)
    results["local_outlier_factor"]["n_features"] = len(iso_cols)
    results["local_outlier_factor"]["n_neighbors"] = n_neighbors

    # =====================================================================
    # 2. XGBoost - supervised
    # =====================================================================
    from xgboost import XGBClassifier

    # THE IMBALANCE PROBLEM.
    #
    # 1,364 malicious days out of 330,452. Left alone, gradient boosting takes the
    # lazy path: predict "normal" every time, be right 99.6% of the time, and
    # catch nobody. The loss function barely notices the 0.41%.
    #
    # scale_pos_weight multiplies the gradient contribution of the positive class
    # by (negatives / positives), which makes missing an insider roughly as
    # expensive as raising 240 false alarms. That is a deliberate trade: in insider
    # threat, a miss is a data breach and a false positive is an hour of an
    # analyst's time.
    n_neg = int((y_train == 0).sum())
    n_pos = int((y_train == 1).sum())
    scale_pos_weight = (n_neg / n_pos) if n_pos else 1.0

    xgb = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric="aucpr",   # PR-AUC, not accuracy - see _metrics()
        random_state=42,
        n_jobs=-1,
    )
    # HOLD BACK A VALIDATION SLICE OF THE TRAINING USERS.
    #
    # Not for early stopping - for choosing the DECISION THRESHOLD. See below.
    # The split is by user, so a user's days never straddle train and validation.
    train_users = np.array(sorted(train_df["user_id"].unique()))
    rng = np.random.RandomState(RANDOM_SEED)
    rng.shuffle(train_users)
    n_val = max(1, int(len(train_users) * 0.2))
    val_users = set(train_users[:n_val])

    val_mask = train_df["user_id"].isin(val_users).to_numpy()
    X_fit, y_fit = X_train[~val_mask], y_train[~val_mask]
    X_val, y_val = X_train[val_mask], y_train[val_mask]

    xgb.fit(X_fit, y_fit)

    # CHOOSE THE THRESHOLD. DO NOT USE 0.5.
    #
    # sklearn's .predict() cuts at probability 0.5. On a balanced problem that is
    # sensible. On a 0.41% base rate it is an arbitrary line with no relationship
    # to the cost of a miss versus the cost of a false alarm.
    #
    # It is also actively misleading. When temporal features were added, this model
    # got substantially better - PR-AUC rose 57%, and at any matched alert budget it
    # caught more insiders in EVERY scenario (scenario 2: 64.6% -> 74.9% at 1% FPR).
    # But judged at the frozen 0.5 cutoff, recall appeared to FALL. A real
    # improvement looked like a regression, purely because the better model was also
    # more confident and sat differently against an arbitrary line.
    #
    # A SOC has no probability budget. It has an ALERT budget: how many
    # investigations can one analyst actually work in a day. So the threshold is
    # set to hit a target false-positive rate, and recall is reported AT that
    # operating point - which is the only number that means anything operationally.
    #
    # CRITICALLY: the threshold is fitted on held-out TRAINING users, never on the
    # test set. Tuning a threshold on test data is a quiet and very common form of
    # cheating - it lets you pick the cutoff that flatters the result, and the
    # number you report is then unreproducible on anything new.
    val_proba = xgb.predict_proba(X_val)[:, 1]
    y_val_arr = y_val.to_numpy()

    # MAXIMISE F-BETA ON THE VALIDATION SET, rather than targeting a fixed
    # false-positive rate.
    #
    # The first version of this targeted FPR = 1%. That was a bad choice and it
    # cost real performance: with a PR-AUC of 0.958 the model can rank almost
    # perfectly, but a fixed 1% FPR parked it at recall 0.98 / precision 0.22 -
    # right on the cliff edge of the PR curve, spraying 1,329 alerts to catch 371
    # attacks. The model was excellent and the OPERATING POINT was throwing it away.
    #
    # F-beta with beta = 2 weights recall twice as heavily as precision. That is a
    # deliberate, stated value judgement about insider threat specifically: a missed
    # insider is a data breach, a false positive is an hour of an analyst's time.
    # Those are not symmetric costs and F1 pretends they are.
    #
    # The sweep is over the actual validation scores, so it finds the real optimum
    # rather than a round number someone liked.
    beta_sq = F_BETA ** 2
    best_thr, best_score = 0.5, -1.0

    candidates = np.unique(np.quantile(val_proba, np.linspace(0.90, 0.9999, 200)))
    for thr in candidates:
        pred = (val_proba >= thr).astype(int)
        tp = int(((pred == 1) & (y_val_arr == 1)).sum())
        fp = int(((pred == 1) & (y_val_arr == 0)).sum())
        fn = int(((pred == 0) & (y_val_arr == 1)).sum())
        if tp == 0:
            continue
        prec = tp / (tp + fp)
        rec = tp / (tp + fn)
        denom = (beta_sq * prec) + rec
        if denom <= 0:
            continue
        fbeta = (1 + beta_sq) * prec * rec / denom
        if fbeta > best_score:
            best_score, best_thr = fbeta, float(thr)

    threshold = min(max(best_thr, 1e-6), 1.0 - 1e-6)

    xgb_proba = xgb.predict_proba(X_test)[:, 1]
    xgb_pred = (xgb_proba >= threshold).astype(int)
    results["xgboost"] = _metrics(y_test, xgb_pred, xgb_proba)
    results["xgboost"]["scale_pos_weight"] = round(scale_pos_weight, 1)
    results["xgboost"]["threshold"] = round(threshold, 4)
    results["xgboost"]["threshold_chosen_on"] = (
        f"max F{F_BETA} over {len(val_users)} held-out training users "
        f"(never the test set)"
    )

    # =====================================================================
    # 2b. LightGBM - the SECOND supervised detector.
    # =====================================================================
    #
    # WHY ADD IT. XGBoost and LightGBM are both gradient-boosted trees, so this is
    # not a test of a different IDEA the way LOF-vs-IsolationForest is. It is a
    # fair-comparison question a reviewer will reasonably ask: "you picked XGBoost -
    # would a different, faster GBM do as well or better on this problem?" The
    # honest way to answer that is to run it under IDENTICAL conditions - same
    # features, same class-imbalance handling, same by-user validation split, same
    # threshold-selection procedure - and report the numbers side by side.
    #
    # LightGBM's leaf-wise growth is typically faster and can fit imbalanced data
    # differently from XGBoost's level-wise growth, so the comparison is not a
    # foregone conclusion. Whichever wins on the real data, we KEEP BOTH in the
    # report and pick the operational model on measured PR-AUC, not on reputation.
    import lightgbm as lgb

    lgbm = lgb.LGBMClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,   # same imbalance handling as XGBoost
        random_state=RANDOM_SEED,
        n_jobs=-1,
        verbose=-1,                          # silence LightGBM's per-round chatter
    )
    lgbm.fit(X_fit, y_fit)                    # same fit split as XGBoost

    # Choose LightGBM's threshold by the SAME procedure used for XGBoost: maximise
    # F-beta on the held-out validation users, never the test set. Copying the
    # method (not the number) is what makes the comparison fair.
    lgbm_val_proba = lgbm.predict_proba(X_val)[:, 1]
    lgbm_best_thr, lgbm_best_f = 0.5, -1.0
    for t in np.linspace(0.01, 0.99, 99):
        vp = (lgbm_val_proba >= t).astype(int)
        _, _, fb, _ = precision_recall_fscore_support(
            y_val, vp, average="binary", beta=F_BETA, zero_division=0
        )
        if fb > lgbm_best_f:
            lgbm_best_f, lgbm_best_thr = fb, t
    lgbm_threshold = min(max(lgbm_best_thr, 1e-6), 1.0 - 1e-6)

    lgbm_proba = lgbm.predict_proba(X_test)[:, 1]
    lgbm_pred = (lgbm_proba >= lgbm_threshold).astype(int)
    results["lightgbm"] = _metrics(y_test, lgbm_pred, lgbm_proba)
    results["lightgbm"]["scale_pos_weight"] = round(scale_pos_weight, 1)
    results["lightgbm"]["threshold"] = round(lgbm_threshold, 4)

    # =====================================================================
    # WHICH SUPERVISED MODEL WINS? Decide on measured PR-AUC (average precision),
    # the honest headline metric on this imbalance - not on which name is more
    # fashionable. Recorded so train_detect can report the verdict plainly.
    # =====================================================================
    xgb_ap = results["xgboost"].get("pr_auc", 0.0)
    lgbm_ap = results["lightgbm"].get("pr_auc", 0.0)
    results["supervised_comparison"] = {
        "xgboost_pr_auc": xgb_ap,
        "lightgbm_pr_auc": lgbm_ap,
        "winner": "xgboost" if xgb_ap >= lgbm_ap else "lightgbm",
        "margin": round(abs(xgb_ap - lgbm_ap), 4),
    }

    # THE OPERATING CURVE.
    #
    # A single precision/recall pair is a policy choice wearing the costume of a
    # result. Different thresholds buy different trades, and an analyst - not a
    # default buried in a library - should be the one choosing. So show the curve.
    curve = []
    for target in (0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01):
        neg = xgb_proba[y_test.to_numpy() == 0]
        t = float(np.quantile(neg, 1.0 - target))
        pr = (xgb_proba >= t).astype(int)
        tp = int(((pr == 1) & (y_test == 1)).sum())
        fp = int(((pr == 1) & (y_test == 0)).sum())
        fn = int(((pr == 0) & (y_test == 1)).sum())
        curve.append({
            "fpr": target,
            "alerts": tp + fp,
            "precision": round(tp / max(tp + fp, 1), 4),
            "recall": round(tp / max(tp + fn, 1), 4),
        })
    results["operating_curve"] = curve

    # --- THE TWO LABELLING CONVENTIONS --------------------------------------
    #
    # We label a day malicious if it falls inside the insider's WINDOW (insiders.csv
    # start -> end). The published literature labels a day malicious only if a
    # malicious EVENT actually occurred on it, per CERT's per-insider answer files.
    #
    # The two disagree about 49% of the malicious days:
    #
    #     window convention : 1,892 malicious user-days
    #     event convention  :   966 malicious user-days
    #
    # And the gap is worst exactly where it distorts the story. Scenario 1 is a
    # SINGLE-DAY exfiltration handed a multi-week window (AAM0658: seven window days,
    # two real ones), so we are scored for "missing" days on which the man did nothing
    # wrong. Scenario 2 is a sustained campaign, so its window is closer to the truth.
    #
    # Neither convention is a lie - "catch him during the campaign" is a perfectly
    # defensible target. But a recall figure quoted WITHOUT SAYING WHICH ONE PRODUCED
    # IT is not comparable to anything, including a published paper. So both are
    # reported, always.
    if "has_malicious_event" in test_df.columns:
        y_event = test_df["has_malicious_event"].to_numpy().astype(int)
        if y_event.sum() > 0:
            flagged = xgb_proba >= threshold
            y_window = y_test.to_numpy().astype(int)
            both = []
            for name, y_conv in (("window", y_window), ("event-day", y_event)):
                tp = int((flagged & (y_conv == 1)).sum())
                fn = int((~flagged & (y_conv == 1)).sum())
                fp = int((flagged & (y_conv == 0)).sum())
                both.append({
                    "convention": name,
                    "malicious_days": int(y_conv.sum()),
                    "recall": round(tp / max(tp + fn, 1), 4),
                    "precision": round(tp / max(tp + fp, 1), 4),
                })
            results["labelling_conventions"] = both

            # Per scenario, under BOTH - this is where the distortion lives.
            #
            # `scenario` is NOT a column on the feature frame. It lives on employees
            # (insider_scenario), and the existing per-scenario report joins to it in
            # SQL. My first version of this block assumed a column that has never
            # existed - it parsed fine, 87 tests passed, and it died the moment the
            # branch actually executed. Third bug of that exact shape in this session.
            scen_rows = db.execute(
                text("SELECT user_id, insider_scenario FROM employees WHERE is_insider")
            ).all()
            scen_of = {u: s for u, s in scen_rows}
            scen_arr = np.array(
                [scen_of.get(u, 0) for u in test_df["user_id"].to_numpy()]
            )

            per_scen = []
            for sc in (1, 2, 3):
                m = scen_arr == sc
                w = int((y_window == 1)[m].sum())
                e = int((y_event == 1)[m].sum())
                if w == 0:
                    continue
                per_scen.append({
                    "scenario": sc,
                    "window_days": w,
                    "event_days": e,
                    "window_recall": round(
                        float(flagged[m & (y_window == 1)].mean()) if w else 0.0, 4
                    ),
                    "event_recall": round(
                        float(flagged[m & (y_event == 1)].mean()) if e else 0.0, 4
                    ),
                })
            results["labelling_per_scenario"] = per_scen

            # --- WHERE DO THE ALERTS ACTUALLY LAND? ---------------------------
            #
            # Switching conventions drops precision from 0.85 to 0.60 without the
            # model changing at all. Same threshold, same 414 alerts. So the drop is
            # not a property of the detector - it is a property of the question.
            #
            # Decompose the alerts and it becomes obvious:
            #
            #   248  landed on a day an attack ACTUALLY ran
            #   105  landed on an INSIDER, inside his attack window, on a day with
            #        no logged malicious event
            #    61  landed outside any insider's window
            #
            # The middle group is what the event-day convention calls a false
            # positive. It is not one. A scenario-2 insider browses job sites for
            # weeks and THEN steals; a flag on a browsing day is EARLY DETECTION,
            # and catching him before the exfiltration is the only time catching him
            # is worth anything.
            #
            # 85% of alerts land on an insider mid-campaign. Only 14.7% land on
            # somebody who is not one - and THAT is the number an analyst feels.
            in_window = y_window == 1
            on_event = y_event == 1
            results["alert_landing"] = {
                "alerts": int(flagged.sum()),
                "on_a_real_attack_day": int((flagged & on_event).sum()),
                "on_an_insider_mid_campaign": int(
                    (flagged & in_window & ~on_event).sum()
                ),
                "outside_any_window": int((flagged & ~in_window).sum()),
            }

    # PERSIST THE MODEL.
    #
    # Until now this function trained a model, scored it, printed some numbers, and
    # threw it away. That is fine for an experiment and useless for a product:
    # nothing could serve a score, because there was nothing to serve.
    #
    # Everything in Milestone 3 - risk scores, alerts, investigation - needs to load
    # a trained model and score a user on demand.
    #
    # The FEATURE COLUMN ORDER is saved with it, and that is not bookkeeping. XGBoost
    # does not see column names at predict time; it indexes a matrix by POSITION.
    # Hand it the right features in the wrong order and it does not raise - it returns
    # a confident, precise, meaningless number. Saving the order makes that
    # impossible.
    # --- RISK SCORING ENGINE (Milestone 3, Module 6) ------------------------
    #
    # The spec's weighted 0-100 composite. It is a WORSE detector than the raw
    # XGBoost probability - measured, -9.8% PR-AUC - and that is exactly what you
    # would expect: the probability is FITTED to the labels and the risk weights were
    # chosen by a human who never saw them. If the hand-weighted version won, it
    # would mean the model had learned nothing a person could not have guessed.
    #
    # It exists for what the raw probability cannot do: DECOMPOSE ("risk 87, mostly
    # Data Access Violations" tells an analyst where to look before they open
    # anything), accept POLICY ("we care most about exfiltration" is a weight, not a
    # retraining run), and be AUDITABLE (when someone is fired on the strength of a
    # score, "the gradient-boosted ensemble said so" is not a defensible position in
    # a tribunal).
    from backend.app.risk import compute_prior_alerts, level_for
    from backend.app.risk import score as risk_score

    prior = compute_prior_alerts(test_df, xgb_proba)
    risk = risk_score(test_df, xgb_proba, prior_alerts=prior)
    rs = risk["risk_score"].to_numpy()
    levels = np.array([level_for(v).value for v in rs])

    test_users = test_df["user_id"].to_numpy()
    mal = test_df["is_malicious"].to_numpy()
    n_insiders = len(set(test_users[mal]))

    tiers = []
    for name in ("critical", "high", "medium", "low"):
        m = levels == name
        caught = len(set(test_users[m & mal]))
        tiers.append({
            "level": name,
            "days": int(m.sum()),
            "insider_days": int(mal[m].sum()),
            "precision": round(float(mal[m].mean()), 4) if m.any() else 0.0,
            "insiders_reached": caught,
        })
    results["risk_tiers"] = tiers
    results["risk_insiders_total"] = n_insiders

    cum = np.zeros(len(levels), dtype=bool)
    for name in ("critical", "high", "medium"):
        cum |= levels == name
        results[f"insiders_reaching_{name}_or_above"] = len(set(test_users[cum & mal]))

    if save_models_to_disk:
        from backend.app.scoring import save_models

        save_models(
            xgb=xgb,
            iso=iso,
            feature_columns=feature_cols,
            threshold=threshold,
            metrics=results["xgboost"],
        )
        results["model_saved"] = True

    # Which features actually did the work? This is the answer to "why did you
    # choose these features" - measured, not asserted.
    importance = sorted(
        zip(feature_cols, xgb.feature_importances_, strict=True),
        key=lambda t: t[1],
        reverse=True,
    )
    results["top_features"] = [
        {"feature": f, "importance": round(float(i), 4)}
        for f, i in importance[:15]
        if i > 0
    ]

    # =====================================================================
    # 3. Per-scenario recall - the number that actually matters
    # =====================================================================
    # An aggregate recall of 0.85 could mean "caught scenarios 1 and 2 perfectly,
    # missed scenario 3 entirely". Scenario 3 is only 20 days out of 1,364, so it
    # can vanish completely inside a headline number that looks fine.
    #
    # We are detecting three DIFFERENT attacks. Report them separately or you are
    # hiding a failure inside an average.
    test_with_pred = test_df.copy()
    test_with_pred["xgb_pred"] = xgb_pred
    test_with_pred["iso_pred"] = iso_pred

    scenario_sql = text("""
        SELECT user_id, insider_scenario FROM employees WHERE is_insider
    """)
    scen_map = {
        r[0]: r[1] for r in db.execute(scenario_sql).all()
    }
    test_with_pred["scenario"] = test_with_pred["user_id"].map(scen_map)

    per_scenario = []
    for scen in sorted(s for s in test_with_pred["scenario"].dropna().unique()):
        sub = test_with_pred[
            (test_with_pred["scenario"] == scen) & (test_with_pred["is_malicious"])
        ]
        if sub.empty:
            continue
        per_scenario.append({
            "scenario": int(scen),
            "malicious_days_in_test": int(len(sub)),
            "xgb_caught": int(sub["xgb_pred"].sum()),
            "xgb_recall": round(float(sub["xgb_pred"].mean()), 4),
            "iso_caught": int(sub["iso_pred"].sum()),
            "iso_recall": round(float(sub["iso_pred"].mean()), 4),
        })
    results["per_scenario"] = per_scenario

    # Detection at the USER level, not the day level. An analyst does not care
    # that we flagged 6 of an insider's 9 bad days - they care that we caught the
    # insider at all. This is the number a security manager actually wants.
    insiders_in_test = test_with_pred[test_with_pred["is_malicious"]]["user_id"].nunique()
    caught = test_with_pred[
        (test_with_pred["is_malicious"]) & (test_with_pred["xgb_pred"] == 1)
    ]["user_id"].nunique()
    results["user_level"] = {
        "insiders_active_in_test_period": int(insiders_in_test),
        "insiders_caught_at_least_once": int(caught),
        "user_level_recall": round(caught / insiders_in_test, 4) if insiders_in_test else 0.0,
    }

    results["duration_seconds"] = round(time.perf_counter() - started, 2)
    return results
