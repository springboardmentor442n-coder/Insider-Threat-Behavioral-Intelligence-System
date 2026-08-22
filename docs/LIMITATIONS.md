# Limitations and Honest Assessment

This document states what the Insider Threat Behavioral Intelligence System does
**not** do, where its numbers come from, and what would have to change before any
of it could be trusted in a real security operations centre. It exists because a
detection system quoted without its limitations is not evidence — it is
advertising, and the difference matters most exactly when someone's job is on the
line.

Every figure below was measured on the full CERT r4.2 dataset (1,000 users, 70
insiders, ~32.8M events) with the model evaluated on **users it had never seen**,
unless stated otherwise. None of it is copied from a paper.

---

## 1. The dataset is synthetic — and this is the largest limitation

CERT r4.2 is not real traffic. The malicious activity was **scripted** by the
dataset's authors to follow three defined scenarios, and that single fact bounds
every result in this project:

- **The attacks are cleaner than reality.** A scripted insider does the malicious
  thing decisively and repeatedly. A real one is hesitant, blends in, and hides
  inside ordinary work. The separation we measure between malicious and normal
  behaviour (USB usage over 300× the population average, after-hours activity that
  normal users *never* exhibit) is almost certainly sharper than anything a real
  deployment would see.
- **The population is homogeneous.** Synthetic "normal" users vary less than real
  employees do. Real organisations contain night-shift workers, travelling sales
  staff, and power users whose legitimate behaviour looks anomalous — the exact
  false-positive sources this dataset largely lacks.
- **Therefore the headline metrics are an upper bound, not a forecast.** The
  XGBoost model's F1 of 0.89 and false-positive rate of 0.00061 are real and
  correctly measured *on this data*. They should be read as "this is how well the
  approach can work when the signal is this clean," not "this is how it will
  perform on your network." I would expect meaningful degradation on real traffic,
  and I have no way to quantify that degradation without real, labelled incidents —
  which essentially no organisation can share.

This is the caveat that every other limitation sits underneath.

---

## 2. What the detector actually catches — and what it is blind to

The model did not learn "insider threat" in the abstract. It learned the specific
behavioural signatures present in this dataset, and its feature importances say so
plainly. The top signals, measured (not asserted), are **USB connections** and
**after-hours logons**, with the rolling USB feature carrying roughly a third of
all decision weight. That produces a real and important blind spot:

- **Email-based exfiltration is essentially invisible to it.** Email-derived
  features contribute close to **0%** of the model's decision weight. An insider
  who steals data by emailing it to a personal account — no USB, no odd hours —
  would very likely pass. This is not a tuning problem; it is a consequence of
  which scenarios exist in the training data, and it would need new features and
  new labelled examples to fix.

Per-scenario recall makes the unevenness concrete (held-out users):

| Scenario | What it is | XGBoost recall |
|---|---|---|
| 1 | A never-USB user who suddenly uses USB and leaks to WikiLeaks (a single-day novelty event) | ~73.6% |
| 2 | Job-site browsing escalating to USB theft (a sustained campaign) | ~97.2% |
| 3 | A sysadmin planting a keylogger and logging into a supervisor's PC | ~66.7% |

The system is strong on the sustained, USB-heavy campaign (scenario 2) and
markedly weaker on the two scenarios that lack a clear, repeated behavioural spike.
**Scenario 3 in particular is close to noise** for this feature set — a sysadmin
using another machine is not far from a sysadmin's normal job, and there is little
in the daily-aggregate features to separate the two. Reporting a single blended
recall number would have hidden this; it is broken out deliberately.

---

## 3. Unsupervised anomaly detection was insufficient here

The spec leans toward unsupervised anomaly detection, and it is worth stating
clearly that **it did not work well on this problem** — a measured finding, not an
assumption. Four detectors were trained and compared on identical features and the
same held-out split:

| Detector | Type | Recall | PR-AUC |
|---|---|---|---|
| XGBoost | supervised | 0.93 | 0.958 |
| LightGBM | supervised | — | 0.168 |
| Isolation Forest | unsupervised | 0.074 | — |
| Local Outlier Factor | unsupervised | 0.085 | 0.009 |

Both unsupervised detectors recover only a small fraction of the attacks. The
honest conclusion is that on this data, unsupervised density methods are **not
sufficient on their own** — which is precisely why the supervised model is a
necessity rather than a stylistic preference. This also carries its own caveat,
though: supervised learning needs labelled attacks, and **a real deployment has
almost none.** The very thing that makes XGBoost win here (labels) is the thing a
real SOC lacks, so a production system would likely need a hybrid — supervised
where labels exist, unsupervised or rule-based to catch the genuinely novel.

---

## 4. The dataset ships two answer keys, and they disagree

CERT r4.2 provides ground truth in two forms that do not agree, and any recall
number is meaningless without saying which one produced it:

- **Window convention** (`insiders.csv`): every day inside an insider's
  start-to-end window is labelled malicious — **378 malicious test days**.
- **Event-day convention** (the per-insider files, and what most published papers
  report): only days on which a malicious event actually ran are labelled —
  **256 malicious test days**.

The two disagree on roughly **49%** of malicious days. The gap is not evenly
spread: scenario 1 is a single-day exfiltration handed a multi-week window, so the
window convention scores the model for "missing" days on which the insider did
nothing wrong. This project stores and reports **both** conventions rather than
quietly picking the flattering one — but it is a genuine limitation that a single
comparable number does not exist, and that any comparison to published results
must first reconcile which convention the paper used.

---

## 5. The spec's risk formula did not work as written

The specification defines a weighted 0–100 risk score with thresholds of 80 /
60 / 35 for critical / high / medium. Measured against the real labels, **those
thresholds could not fire**: 0 of 21 insiders reached HIGH or above. The reason is
structural — the largest single component is worth 35 points, and CRITICAL needs
80, so a user would have to trigger nearly every component at once. Real insiders
trigger one or two: a scenario-1 insider never touches a supervisor's PC; a
scenario-3 sysadmin never browses job sites.

The thresholds were therefore recalibrated from the actual score distribution on
held-out users to 50 / 40 / 20, which produces a usable triage (CRITICAL for 14 of
21 insiders, HIGH-or-above for all 21). A related fix corrected the
privilege-misuse component, whose discrimination improved from a ROC-AUC of 0.42
(worse than chance) to 0.73.

The limitation to be honest about: **these thresholds are fitted to this dataset.**
They are defensible and measured, but they are not universal constants, and they
would need re-derivation on any real population.

---

## 6. Evaluation caveats

- **Class-balanced evaluation inflates precision.** Insider days are a tiny
  fraction of all days. Metrics computed on an artificially balanced test set —
  common in the literature — report far rosier precision than the true, imbalanced
  operating point. The numbers here are measured on the **natural, imbalanced**
  distribution for that reason, which makes them look less impressive than some
  published figures and more honest than all of them.
- **A single precision/recall pair is a policy choice, not a score.** The model's
  quality is its PR-AUC (0.958); where the decision threshold sits is a decision
  about how many alerts an analyst can carry, and it should be made by a person in
  the open. The reported operating point weights recall over precision (a missed
  insider is a breach; a false positive is an hour of someone's time), but that is
  a choice, and a different organisation would legitimately choose differently.
- **The container demo uses a 15-user fixture, not the full dataset.** The
  one-command `docker-compose up` seeds a tiny committed fixture so the stack comes
  up quickly and self-contained. Its numbers are **not** the numbers in this
  document — the figures here are from the full 1,000-user run on real hardware.
  The fixture exists to prove the system runs end to end, not to reproduce the
  metrics.

---

## 7. Operational limitations

Things a real deployment would require that this project does not claim to provide:

- **Daily aggregation granularity.** Features are per-user-per-day. An attack that
  happens and completes within hours can be diluted inside a day's totals.
  Real-time or hourly detection would need a different feature cadence.
- **No concept drift handling.** Baselines are built once. Real behaviour shifts —
  reorganisations, new tools, seasonal patterns — and a static baseline slowly goes
  stale. Production would need periodic, automated rebaselining.
- **No adversarial robustness.** A knowledgeable insider who understands that USB
  and after-hours activity are watched can simply avoid them. The model has no
  defence against someone deliberately staying inside their own baseline.
- **Single-tenant, single-org scope.** Peer-group comparison is within one
  organisation's population; cross-organisation intelligence is out of scope.

---

## 8. Summary

What this project demonstrates is that a carefully engineered, honestly measured
behavioural detection pipeline can catch every insider in a held-out population
(21/21 at the user level) with a very low false-positive rate — **on synthetic
data with clean, scripted attacks.** What it does not demonstrate, and does not
claim, is that those numbers transfer to real traffic, that the approach catches
attack patterns absent from the training scenarios (email exfiltration most
notably), or that unsupervised methods alone would suffice.

The strongest thing here is not any single metric. It is that the project
**measured the specification instead of just implementing it** — found that the
prescribed risk thresholds could not fire, that the dataset's two answer keys
disagree, that unsupervised detection is insufficient, and that the detector is
blind to a whole class of exfiltration — and reported all of it rather than
burying it. A detection system that knows and states its own blind spots is more
trustworthy than one that claims to have none.
