"""Train the insider-threat detection model and persist all artefacts.

Produces, in ml_model/:
    gb.pkl              trained Gradient Boosting classifier
    scaler.pkl          MinMaxScaler fitted on the training split
    feature_columns.pkl ordered feature list the model expects
    feature_means.pkl   population baseline means
    baselines.pkl       per-user behavioural baselines (UEBA)
    metrics.json        held-out evaluation metrics
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    auc,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils.class_weight import compute_sample_weight

from config import Config
from app.ml.features import FEATURE_COLUMNS, load_features
from app.ml import ueba

TEST_FRACTION = 0.30


def _build_model(backend: str, y_train: pd.Series):
    """Gradient Boosting is the default; XGBoost is used when available."""
    if backend == "xgboost":
        import xgboost as xgb  # noqa: PLC0415

        neg, pos = int((y_train == 0).sum()), int((y_train == 1).sum())
        return xgb.XGBClassifier(
            n_estimators=150,
            max_depth=6,
            learning_rate=0.05,
            scale_pos_weight=(neg / pos) if pos else 1.0,
            random_state=42,
            eval_metric="aucpr",
        )
    return GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        random_state=42,
    )


def _resolve_backend(requested: str) -> str:
    if requested == "gb":
        return "gb"
    try:
        import xgboost  # noqa: F401,PLC0415

        return "xgboost"
    except Exception as exc:  # native libomp is frequently absent
        if requested == "xgboost":
            print(f"  XGBoost unavailable ({type(exc).__name__}) — falling back to sklearn GB")
        return "gb"


def train(
    features_csv: str | Path | None = None,
    model_dir: str | Path | None = None,
    backend: str = "auto",
    verbose: bool = True,
) -> dict:
    features_csv = Path(features_csv or Config.FEATURES_CSV)
    model_dir = Path(model_dir or Config.MODEL_DIR)
    model_dir.mkdir(parents=True, exist_ok=True)

    def log(msg):
        if verbose:
            print(f"  {msg}")

    df = load_features(features_csv)
    log(f"Loaded {len(df):,} user-days | {df['user'].nunique():,} users "
        f"| {int(df['is_insider'].sum()):,} malicious")

    if df["is_insider"].sum() < 2:
        raise ValueError(
            "Fewer than 2 positive labels — cannot train. Regenerate the dataset "
            "with a higher --insider-rate or supply the CERT answers/ key."
        )

    # Chronological split: the model must be judged on days it has never seen,
    # exactly as it would be in production. A random split would leak future
    # behaviour of the same user into training.
    df = df.sort_values("day").reset_index(drop=True)
    split_idx = int(len(df) * (1 - TEST_FRACTION))
    train_df, test_df = df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()

    X_train, y_train = train_df[FEATURE_COLUMNS], train_df["is_insider"]
    X_test, y_test = test_df[FEATURE_COLUMNS], test_df["is_insider"]
    log(f"Train: {len(X_train):,} rows / {int(y_train.sum())} positive | "
        f"Test: {len(X_test):,} rows / {int(y_test.sum())} positive")

    if y_train.sum() == 0 or y_test.sum() == 0:
        raise ValueError(
            "The chronological split left one side without positive labels. "
            "Generate a longer date range so malicious windows fall on both sides."
        )

    scaler = MinMaxScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    resolved = _resolve_backend(backend)
    model = _build_model(resolved, y_train)
    log(f"Fitting {type(model).__name__} ...")
    if resolved == "gb":
        # sklearn's GB has no scale_pos_weight, so rebalance via sample weights.
        model.fit(X_train_s, y_train,
                  sample_weight=compute_sample_weight("balanced", y_train))
    else:
        model.fit(X_train_s, y_train)

    y_prob = model.predict_proba(X_test_s)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    precision, recall, _ = precision_recall_curve(y_test, y_prob)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()

    flagged_users = set(test_df.loc[y_pred == 1, "user"])
    true_users = set(test_df.loc[y_test == 1, "user"])

    metrics = {
        "backend": resolved,
        "model": type(model).__name__,
        "n_rows": int(len(df)),
        "n_users": int(df["user"].nunique()),
        "n_features": len(FEATURE_COLUMNS),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "train_positives": int(y_train.sum()),
        "test_positives": int(y_test.sum()),
        "pr_auc": round(float(auc(recall, precision)), 4),
        "average_precision": round(float(average_precision_score(y_test, y_prob)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "user_level_recall": (
            f"{len(flagged_users & true_users)}/{len(true_users)}" if true_users else "n/a"
        ),
        "date_range": [str(df["day"].min().date()), str(df["day"].max().date())],
    }

    importances = getattr(model, "feature_importances_", np.zeros(len(FEATURE_COLUMNS)))
    metrics["feature_importance"] = {
        f: round(float(v), 5)
        for f, v in sorted(
            zip(FEATURE_COLUMNS, importances), key=lambda kv: kv[1], reverse=True
        )
    }

    log(f"PR-AUC {metrics['pr_auc']} | ROC-AUC {metrics['roc_auc']} | "
        f"P {metrics['precision']} | R {metrics['recall']} | F1 {metrics['f1']}")
    log(f"User-level recall: {metrics['user_level_recall']}")

    # Baselines are built on the training window only — the UEBA engine must
    # not know what a user is going to do in the evaluation period.
    baselines = ueba.build_baselines(train_df)
    pop_means = ueba.population_means(train_df)

    artefacts = {
        "gb.pkl": model,
        "scaler.pkl": scaler,
        "feature_columns.pkl": FEATURE_COLUMNS,
        "feature_means.pkl": pop_means,
        "baselines.pkl": baselines,
    }
    for name, obj in artefacts.items():
        with open(model_dir / name, "wb") as fh:
            pickle.dump(obj, fh)
    (model_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    log(f"Saved {len(artefacts) + 1} artefacts to {model_dir}")

    return metrics


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--features", default=None)
    ap.add_argument("--backend", choices=["auto", "gb", "xgboost"], default="auto")
    args = ap.parse_args()
    train(features_csv=args.features, backend=args.backend)
