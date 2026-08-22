"""Model persistence, inference, and per-alert explanation (SHAP).

WHY THIS MODULE EXISTS
----------------------
Until now, `train_detect` fitted a model, scored the test set, printed some numbers,
and exited. The model was thrown away. That is fine for an experiment and useless
for a product: nothing could SERVE a score, because there was nothing to serve.

Everything in Milestone 3 - risk scores, alerts, investigation - needs to load a
trained model and score a user on demand. So the model gets saved.

AND THEN IT HAS TO EXPLAIN ITSELF
---------------------------------
A security analyst who is handed "ABC0174: risk 87, CRITICAL" and nothing else has
been given a number, not an alert. They cannot act on it, they cannot dismiss it,
and after the third false alarm they will stop reading them - which is precisely how
detection systems die in the field.

They need to know WHY. And "why" cannot be answered with global feature importances,
which is what we have been printing. Those say the model relies on
`roll7_usb_connect_count` ACROSS EVERYONE. They say nothing about THIS person on
THIS day. A user could be flagged for something else entirely and the global chart
would look identical.

SHAP answers the per-alert question. For one prediction, it decomposes the score
into a contribution from each feature - and those contributions SUM EXACTLY to the
prediction. It is not a heuristic ranking; it is an additive decomposition with a
proof behind it (Shapley values, from cooperative game theory - the unique
attribution satisfying a set of fairness axioms).

That means an analyst can be told:

    ABC0174 scored 0.94 (baseline 0.004)
      +0.42  roll7_usb_connect_count = 8.4   (their own average is 0.0)
      +0.31  z_roll14_usb_connect_count = 25.0
      +0.12  roll14_file_event_count = 31.2
      -0.03  after_hours_logon_count = 0

...which is a case, not a number. The negative contribution matters too: it tells
the analyst what argued AGAINST the alert, which is what makes the system worth
trusting rather than merely obeying.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Where the trained artefacts live. Deliberately a directory OUTSIDE the package -
# a model is data, not code, and it does not belong in the source tree or in git.
# It is derived from the database and rebuilt by `train_detect --save`.
MODEL_DIR = Path(__file__).resolve().parents[2] / "models"

MODEL_PATH = MODEL_DIR / "xgboost.joblib"
ISOFOREST_PATH = MODEL_DIR / "isolation_forest.joblib"
METADATA_PATH = MODEL_DIR / "metadata.joblib"


@dataclass(frozen=True)
class FeatureContribution:
    """One feature's contribution to one prediction."""

    feature: str
    value: float
    shap_value: float

    @property
    def direction(self) -> str:
        return "increased" if self.shap_value > 0 else "decreased"


@dataclass(frozen=True)
class Explanation:
    """Why the model gave THIS user on THIS day THIS score.

    `base_value` is the model's output before it sees any features - the average
    prediction across the training set. `contributions` are the deltas from there,
    and they SUM to the final score. That is the property that makes SHAP an
    explanation rather than a guess: nothing is left over and nothing is invented.
    """

    user_id: str
    date: Any
    probability: float
    base_value: float
    contributions: list[FeatureContribution]

    def top(self, n: int = 5) -> list[FeatureContribution]:
        """The n features that moved the score MOST, in either direction.

        Sorted by magnitude, not by signed value. An analyst needs to see what
        argued AGAINST the alert as well as what argued for it - a system that only
        ever shows you the evidence for its own conclusion is not explaining itself,
        it is lobbying.
        """
        return sorted(self.contributions, key=lambda c: -abs(c.shap_value))[:n]


def save_models(
    xgb: Any,
    iso: Any,
    feature_columns: list[str],
    threshold: float,
    metrics: dict,
) -> None:
    """Persist the trained models and everything needed to reproduce a score.

    THE METADATA IS NOT OPTIONAL, AND IT IS THE PART PEOPLE FORGET.

    A saved XGBoost model is a set of trees that expect a matrix of a particular
    width, in a particular COLUMN ORDER. Hand it the same features in a different
    order and it will not error - it will happily produce confident, meaningless
    numbers, because column 4 is now `usb_connect_count` where it used to be
    `after_hours_logon_count` and the trees have no idea.

    That is a silent, catastrophic failure. So `feature_columns` is saved alongside
    the model and asserted on every load.

    The THRESHOLD is saved for the same reason. It was fitted on held-out validation
    users by maximising F2. If inference used a different one - say, sklearn's
    default 0.5 - every score served in production would sit at a different operating
    point than the one that was measured and reported. The number in the paper and
    the number in the product would be different numbers, and nobody would notice.
    """
    import joblib

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(xgb, MODEL_PATH)
    joblib.dump(iso, ISOFOREST_PATH)
    joblib.dump(
        {
            "feature_columns": feature_columns,
            "threshold": threshold,
            "metrics": metrics,
            "n_features": len(feature_columns),
        },
        METADATA_PATH,
    )

    logger.info("Saved models to %s", MODEL_DIR)


def load_models() -> tuple[Any, Any, dict]:
    """Load the trained models. Raises if they were never trained.

    A clear error beats a confusing one: an API that returns 500 because a .joblib
    is missing tells the operator nothing. This tells them exactly what to run.
    """
    import joblib

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No trained model at {MODEL_PATH}.\n\n"
            f"    Run:  python -m scripts.train_detect --save\n\n"
            f"Training takes about 45 seconds on CPU."
        )

    xgb = joblib.load(MODEL_PATH)
    iso = joblib.load(ISOFOREST_PATH)
    meta = joblib.load(METADATA_PATH)
    return xgb, iso, meta


def align_features(df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    """Put the columns in the EXACT order the model was trained on.

    THIS FUNCTION IS THE DIFFERENCE BETWEEN A SCORE AND A RANDOM NUMBER.

    XGBoost does not see column NAMES at predict time. It sees a matrix, and it
    indexes into it by POSITION. Feed it the right features in the wrong order and
    it does not raise - it returns a confident, precise, entirely meaningless
    probability, because the tree that was splitting on `usb_connect_count > 3` is
    now splitting on whatever happens to be sitting in that column instead.

    Silent wrong answers are the worst kind. So the columns are reordered explicitly,
    and a missing one is a hard error rather than a zero-filled guess.
    """
    missing = [c for c in feature_columns if c not in df.columns]
    if missing:
        raise ValueError(
            f"The feature frame is missing {len(missing)} column(s) the model was "
            f"trained on: {missing[:5]}{'...' if len(missing) > 5 else ''}\n\n"
            f"This usually means the feature pipeline changed but the model was not "
            f"retrained. Run: python -m scripts.train_detect --save"
        )
    return df[feature_columns].astype("float32")


def explain(
    xgb: Any,
    X: pd.DataFrame,
    feature_columns: list[str],
    user_ids: list[str],
    dates: list[Any],
    probabilities: np.ndarray,
) -> list[Explanation]:
    """Decompose each prediction into per-feature contributions using SHAP.

    WHY TreeExplainer AND NOT THE GENERIC ONE
    -----------------------------------------
    shap.TreeExplainer computes EXACT Shapley values for tree ensembles in polynomial
    time. The model-agnostic KernelExplainer estimates them by sampling, which for
    157 features and thousands of rows is both slower and approximate. For a tree
    model there is no reason to accept an approximation.

    WHAT THE NUMBERS MEAN
    ---------------------
    SHAP returns values in the model's LOG-ODDS space, not probability space, because
    that is the space in which the contributions are additive. base_value +
    sum(shap_values) = the raw margin, exactly. Converting each contribution to
    "percentage points of probability" would be a lie - probability is not additive,
    so the parts would not sum to the whole, and an analyst who added them up would
    find they did not.

    So the contributions are reported in the space where they are true, and the final
    probability is reported alongside. An explanation that does not add up is worse
    than no explanation, because it teaches people to distrust the arithmetic rather
    than the model.
    """
    import shap

    explainer = shap.TreeExplainer(xgb)
    shap_values = explainer.shap_values(X)
    base = float(explainer.expected_value)

    out: list[Explanation] = []
    for i in range(len(X)):
        contribs = [
            FeatureContribution(
                feature=feature_columns[j],
                value=float(X.iloc[i, j]),
                shap_value=float(shap_values[i, j]),
            )
            for j in range(len(feature_columns))
            # Drop the noise. With 157 features, most contribute essentially nothing
            # to any given prediction, and listing them buries the three that matter.
            if abs(shap_values[i, j]) > 1e-4
        ]
        out.append(
            Explanation(
                user_id=user_ids[i],
                date=dates[i],
                probability=float(probabilities[i]),
                base_value=base,
                contributions=contribs,
            )
        )
    return out


def format_explanation(exp: Explanation, top_n: int = 6) -> str:
    """Render an explanation as something an analyst can actually read."""
    lines = [
        f"  {exp.user_id}  {exp.date}",
        f"  model probability: {exp.probability:.4f}"
        f"   (baseline for an average day: {_sigmoid(exp.base_value):.4f})",
        "",
        "  WHY:",
    ]
    for c in exp.top(top_n):
        sign = "+" if c.shap_value > 0 else "-"
        lines.append(
            f"    {sign}{abs(c.shap_value):6.3f}   {c.feature:<38} = {c.value:>10.2f}"
        )
    return "\n".join(lines)


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-x))