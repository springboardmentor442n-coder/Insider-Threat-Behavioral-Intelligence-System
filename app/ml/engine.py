"""Runtime scoring engine — loads the trained artefacts and serves inference.

A single `ThreatEngine` instance is created at app start-up. It holds the
scored feature table in memory, which is what every API endpoint reads from.
"""

from __future__ import annotations

import json
import pickle
import threading
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from config import Config
from app.ml import ueba
from app.ml.features import (
    BEHAVIOURAL_COLUMNS,
    FEATURE_COLUMNS,
    FEATURE_LABELS,
    load_features,
)


class ModelNotTrained(RuntimeError):
    """Raised when artefacts are missing — the caller should run the pipeline."""


class ThreatEngine:
    def __init__(self, model_dir: Path | None = None, features_csv: Path | None = None):
        self.model_dir = Path(model_dir or Config.MODEL_DIR)
        self.features_csv = Path(features_csv or Config.FEATURES_CSV)
        self._lock = threading.RLock()
        self._explainer = None
        self._explainer_failed = False
        self.loaded_at: datetime | None = None
        self.load()

    # ------------------------------------------------------------------
    # Loading & scoring
    # ------------------------------------------------------------------
    def load(self):
        required = ["gb.pkl", "scaler.pkl", "feature_columns.pkl", "baselines.pkl"]
        missing = [f for f in required if not (self.model_dir / f).exists()]
        if missing or not self.features_csv.exists():
            raise ModelNotTrained(
                f"Missing artefacts: {', '.join(missing) or self.features_csv.name}. "
                "Run `python scripts/bootstrap.py` first."
            )

        with self._lock:
            self.model = self._unpickle("gb.pkl")
            self.scaler = self._unpickle("scaler.pkl")
            self.feature_columns = self._unpickle("feature_columns.pkl")
            self.baselines = self._unpickle("baselines.pkl")
            try:
                self.pop_means = self._unpickle("feature_means.pkl")
            except FileNotFoundError:
                self.pop_means = pd.Series(dtype=float)

            metrics_path = self.model_dir / "metrics.json"
            self.metrics = (
                json.loads(metrics_path.read_text()) if metrics_path.exists() else {}
            )

            self.df = load_features(self.features_csv)
            self._score()
            self._explainer = None
            self._explainer_failed = False
            self.loaded_at = datetime.now(timezone.utc).replace(tzinfo=None)

    def _unpickle(self, name: str):
        path = self.model_dir / name
        if not path.exists():
            raise FileNotFoundError(str(path))
        with open(path, "rb") as fh:
            return pickle.load(fh)

    def _score(self):
        """Score every user-day once; endpoints then just slice this table."""
        df = self.df
        X = df[self.feature_columns]
        df["ml_probability"] = self.model.predict_proba(self.scaler.transform(X))[:, 1]
        df["ueba_score"] = ueba.behavioural_score(df, self.baselines)
        df["risk_score"] = ueba.composite_score(
            df["ueba_score"].to_numpy(), df["ml_probability"].to_numpy()
        )
        df["severity"] = ueba.severity_series(df["risk_score"].to_numpy())
        df["day_str"] = df["day"].dt.strftime("%Y-%m-%d")

        # Per-user rollup drives the profiles, alerts and dashboard views.
        agg = (
            df.groupby("user")
            .agg(
                peak_risk=("risk_score", "max"),
                mean_risk=("risk_score", "mean"),
                latest_risk=("risk_score", "last"),
                active_days=("day", "count"),
                flagged_days=("risk_score", lambda s: int((s >= Config.ALERT_THRESHOLD).sum())),
                confirmed_days=("is_insider", "sum"),
                first_seen=("day", "min"),
                last_seen=("day", "max"),
            )
            .reset_index()
        )
        agg["severity"] = ueba.severity_series(agg["peak_risk"].to_numpy())
        self.user_summary = agg.sort_values("peak_risk", ascending=False).reset_index(drop=True)

    # ------------------------------------------------------------------
    # Ad-hoc scoring (used by /api/v1/score for what-if analysis)
    # ------------------------------------------------------------------
    def score_record(self, user: str, values: dict) -> dict:
        """Score a hypothetical day for `user`.

        Features the caller omits are filled from that user's own baseline
        (or the population mean for an unknown user) rather than zero. Zeroing
        them would hand the model an off-manifold vector — a day with 40 files
        copied to USB but no logons and no HTTP traffic never occurs in
        training, and the prediction would be meaningless.
        """
        base = self.baselines.loc[user] if user in self.baselines.index else None

        row, defaulted = {}, []
        for col in self.feature_columns:
            if col in values and values[col] is not None:
                row[col] = float(values[col])
                continue
            defaulted.append(col)
            if base is not None and f"{col}_mean" in base.index:
                row[col] = float(base[f"{col}_mean"])
            else:
                row[col] = float(self.pop_means.get(col, 0.0) or 0.0)

        frame = pd.DataFrame([row])[self.feature_columns]
        prob = float(self.model.predict_proba(self.scaler.transform(frame))[0, 1])

        frame["user"] = user
        ueba_score = float(ueba.behavioural_score(frame, self.baselines)[0])
        risk = float(ueba.composite_score(np.array([ueba_score]), np.array([prob]))[0])
        return {
            "user": user,
            "ml_probability": round(prob, 4),
            "ueba_score": round(ueba_score, 2),
            "risk_score": round(risk, 2),
            "severity": ueba.severity(risk),
            "supplied_features": sorted(set(self.feature_columns) - set(defaulted)),
            "defaulted_features": defaulted,
            "baseline_source": "user" if base is not None else "population",
            "inputs": {k: round(v, 3) for k, v in row.items()},
            "contributions": ueba.risk_contributions(frame.iloc[0], self.baselines),
        }

    # ------------------------------------------------------------------
    # Explainability
    # ------------------------------------------------------------------
    def _get_explainer(self):
        if self._explainer is not None or self._explainer_failed:
            return self._explainer
        try:
            import shap  # noqa: PLC0415

            self._explainer = shap.TreeExplainer(self.model)
        except Exception:
            # SHAP is optional at runtime; the UI degrades to model importances.
            self._explainer_failed = True
            self._explainer = None
        return self._explainer

    def explain(self, row: pd.Series, top_n: int = 8) -> dict:
        X = pd.DataFrame([row[self.feature_columns].astype(float)])
        scaled = self.scaler.transform(X)
        explainer = self._get_explainer()

        if explainer is not None:
            try:
                values = np.asarray(explainer.shap_values(scaled))
                # Binary tree models may return (n, features) or (n, features, 2).
                if values.ndim == 3:
                    values = values[..., -1]
                contributions = values[0]
                method = "shap"
            except Exception:
                contributions, method = None, "importance"
        else:
            contributions, method = None, "importance"

        if contributions is None:
            # Fallback: signed importance — magnitude from the model, direction
            # from whether the feature sits above the population mean.
            importances = np.asarray(
                getattr(self.model, "feature_importances_", np.zeros(len(self.feature_columns)))
            )
            direction = np.array(
                [
                    1.0 if float(row.get(f, 0) or 0) >= float(self.pop_means.get(f, 0) or 0) else -1.0
                    for f in self.feature_columns
                ]
            )
            contributions = importances * direction

        items = [
            {
                "feature": f,
                "label": FEATURE_LABELS.get(f, f),
                "value": round(float(row.get(f, 0) or 0), 2),
                "contribution": round(float(c), 5),
                "direction": "increases risk" if c > 0 else "reduces risk",
            }
            for f, c in zip(self.feature_columns, contributions)
        ]
        items.sort(key=lambda d: abs(d["contribution"]), reverse=True)
        return {"method": method, "features": items[:top_n]}

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def users(self) -> pd.DataFrame:
        return self.user_summary

    def user_days(self, user: str) -> pd.DataFrame:
        return self.df[self.df["user"] == user].sort_values("day")

    def worst_day(self, user: str) -> pd.Series | None:
        rows = self.user_days(user)
        if rows.empty:
            return None
        return rows.loc[rows["risk_score"].idxmax()]

    def day_row(self, user: str, day: str | None) -> pd.Series | None:
        rows = self.user_days(user)
        if rows.empty:
            return None
        if day:
            match = rows[rows["day_str"] == day]
            if match.empty:
                return None
            return match.iloc[0]
        return rows.loc[rows["risk_score"].idxmax()]

    def alerts(self, min_score: float | None = None, severity: str | None = None,
               limit: int = 200) -> pd.DataFrame:
        threshold = Config.ALERT_THRESHOLD if min_score is None else min_score
        rows = self.df[self.df["risk_score"] >= threshold]
        if severity:
            rows = rows[rows["severity"] == severity.upper()]
        return rows.sort_values("risk_score", ascending=False).head(limit)

    def stats(self) -> dict:
        df, users = self.df, self.user_summary
        severity_counts = users["severity"].value_counts().to_dict()
        alert_rows = self.alerts()

        daily = (
            df.groupby("day_str")
            .agg(mean_risk=("risk_score", "mean"), max_risk=("risk_score", "max"),
                 alerts=("risk_score", lambda s: int((s >= Config.ALERT_THRESHOLD).sum())))
            .reset_index()
            .tail(60)
        )

        return {
            "total_users": int(df["user"].nunique()),
            "total_user_days": int(len(df)),
            "date_range": [df["day_str"].min(), df["day_str"].max()],
            "open_alerts": int(len(alert_rows)),
            "users_at_risk": int((users["peak_risk"] >= Config.ALERT_THRESHOLD).sum()),
            "confirmed_insiders": int(df.loc[df["is_insider"] == 1, "user"].nunique()),
            "mean_risk": round(float(df["risk_score"].mean()), 2),
            "severity_distribution": {
                k: int(severity_counts.get(k, 0))
                for k in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            },
            "alert_severity_distribution": {
                k: int((alert_rows["severity"] == k).sum())
                for k in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            },
            "risk_timeline": daily.to_dict(orient="records"),
            "top_indicators": self._top_indicators(),
            "model": {
                "name": self.metrics.get("model", "GradientBoostingClassifier"),
                "backend": self.metrics.get("backend", "gb"),
                "pr_auc": self.metrics.get("pr_auc"),
                "roc_auc": self.metrics.get("roc_auc"),
                "precision": self.metrics.get("precision"),
                "recall": self.metrics.get("recall"),
                "f1": self.metrics.get("f1"),
                "features": len(self.feature_columns),
                "loaded_at": self.loaded_at.isoformat() + "Z" if self.loaded_at else None,
            },
        }

    def _top_indicators(self) -> list[dict]:
        """Which weighted indicators drive the current alert population."""
        alert_rows = self.alerts(limit=500)
        if alert_rows.empty:
            return []
        matrix, feats = ueba._weighted_matrix(alert_rows, self.baselines)
        weights = np.array([Config.RISK_WEIGHTS[f] for f in feats])
        totals = (matrix * weights).sum(axis=0)
        total = totals.sum() or 1.0
        out = [
            {
                "feature": f,
                "label": FEATURE_LABELS.get(f, f),
                "weight": float(weights[i]),
                "share": round(float(totals[i] / total * 100), 1),
            }
            for i, f in enumerate(feats)
        ]
        return sorted(out, key=lambda d: d["share"], reverse=True)

    def investigate(self, user: str, day: str | None = None) -> dict:
        row = self.day_row(user, day)
        if row is None:
            return {}
        history = self.user_days(user)
        return {
            "user": user,
            "day": row["day_str"],
            "risk_score": round(float(row["risk_score"]), 2),
            "ueba_score": round(float(row["ueba_score"]), 2),
            "ml_probability": round(float(row["ml_probability"]), 4),
            "severity": row["severity"],
            "confirmed_insider": bool(row["is_insider"]),
            "observed": {c: float(row[c]) for c in BEHAVIOURAL_COLUMNS},
            "deviations": ueba.deviation_report(row, self.baselines, self.pop_means),
            "risk_contributions": ueba.risk_contributions(row, self.baselines),
            "explanation": self.explain(row),
            "timeline": history[
                ["day_str", "risk_score", "ueba_score", "ml_probability", "severity", "is_insider"]
            ]
            .rename(columns={"day_str": "day"})
            .round(3)
            .to_dict(orient="records"),
            "peak_days": history.nlargest(5, "risk_score")[
                ["day_str", "risk_score", "severity"]
            ]
            .rename(columns={"day_str": "day"})
            .round(2)
            .to_dict(orient="records"),
            "baseline_days": int(
                self.baselines.loc[user, "observed_days"]
                if user in self.baselines.index
                else 0
            ),
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
_engine: ThreatEngine | None = None
_engine_error: str | None = None
_paths: tuple = (None, None)


def init_engine(model_dir=None, features_csv=None) -> ThreatEngine | None:
    """Load the engine, tolerating an untrained install so the app still boots.

    Paths are passed in from app.config rather than read off Config here, so a
    test or alternate config object can point the engine somewhere else.
    """
    global _engine, _engine_error, _paths
    _paths = (model_dir, features_csv)
    try:
        _engine = ThreatEngine(model_dir, features_csv)
        _engine_error = None
    except ModelNotTrained as exc:
        _engine, _engine_error = None, str(exc)
    return _engine


def get_engine() -> ThreatEngine:
    if _engine is None:
        raise ModelNotTrained(_engine_error or "Engine not initialised.")
    return _engine


def engine_status() -> dict:
    return {"ready": _engine is not None, "error": _engine_error}


def reload_engine() -> ThreatEngine | None:
    global _engine, _engine_error
    if _engine is not None:
        try:
            _engine.load()
            return _engine
        except ModelNotTrained as exc:
            _engine, _engine_error = None, str(exc)
            return None
    return init_engine(*_paths)
