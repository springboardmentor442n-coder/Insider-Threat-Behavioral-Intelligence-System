"""Core intelligence endpoints: dashboard, profiles, alerts, investigation."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from flask import Blueprint, jsonify, request

from app.auth import current_username, require_auth
from app.extensions import db
from app.ml import engine as eng
from app.ml import ueba
from app.ml.features import BEHAVIOURAL_COLUMNS, FEATURE_LABELS
from app.models import AlertCase, record_audit
from app.services.directory import get_directory
from config import Config

bp = Blueprint("intel", __name__, url_prefix="/api/v1")


def _clean(obj):
    """JSON-safe: pandas/numpy scalars and NaN are not natively serialisable."""
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if hasattr(obj, "item"):
        return _clean(obj.item())
    if isinstance(obj, pd.Timestamp):
        return obj.strftime("%Y-%m-%d")
    return obj


def _engine_or_503():
    try:
        return eng.get_engine(), None
    except eng.ModelNotTrained as exc:
        return None, (
            jsonify({"error": "model not trained", "detail": str(exc)}),
            503,
        )


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@bp.get("/dashboard")
@require_auth("viewer")
def dashboard():
    engine, err = _engine_or_503()
    if err:
        return err
    return jsonify(_clean(engine.stats()))


@bp.get("/model/metrics")
@require_auth("viewer")
def model_metrics():
    engine, err = _engine_or_503()
    if err:
        return err
    return jsonify(_clean(engine.metrics))


@bp.post("/model/reload")
@require_auth("admin")
def model_reload():
    engine = eng.reload_engine()
    record_audit(current_username(), "MODEL_RELOAD")
    if engine is None:
        return jsonify({"error": "reload failed", **eng.engine_status()}), 503
    return jsonify({"status": "reloaded", "model": engine.metrics.get("model")})


# ---------------------------------------------------------------------------
# Employee profiles & behavioural profiling
# ---------------------------------------------------------------------------
@bp.get("/users")
@require_auth("viewer")
def list_users():
    engine, err = _engine_or_503()
    if err:
        return err

    df = engine.users().copy()
    search = (request.args.get("search") or "").strip().upper()
    severity = (request.args.get("severity") or "").strip().upper()
    sort = request.args.get("sort", "peak_risk")
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(int(request.args.get("per_page", 25)), 200)

    directory = get_directory()
    df["name"] = df["user"].map(lambda u: directory.get(u, {}).get("name", ""))
    df["role"] = df["user"].map(lambda u: directory.get(u, {}).get("role", ""))
    df["department"] = df["user"].map(lambda u: directory.get(u, {}).get("department", ""))

    if search:
        df = df[
            df["user"].str.upper().str.contains(search, regex=False)
            | df["name"].str.upper().str.contains(search, regex=False)
        ]
    if severity:
        df = df[df["severity"] == severity]
    if sort in df.columns:
        df = df.sort_values(sort, ascending=(sort in ("user", "name")))

    total = len(df)
    page_rows = df.iloc[(page - 1) * per_page : page * per_page]

    items = []
    for row in page_rows.itertuples(index=False):
        items.append(
            {
                "user": row.user,
                "name": row.name,
                "role": row.role,
                "department": row.department,
                "peak_risk": round(float(row.peak_risk), 2),
                "mean_risk": round(float(row.mean_risk), 2),
                "latest_risk": round(float(row.latest_risk), 2),
                "severity": row.severity,
                "active_days": int(row.active_days),
                "flagged_days": int(row.flagged_days),
                "confirmed_days": int(row.confirmed_days),
                "first_seen": str(pd.Timestamp(row.first_seen).date()),
                "last_seen": str(pd.Timestamp(row.last_seen).date()),
            }
        )

    return jsonify(
        {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": max(math.ceil(total / per_page), 1),
            "items": _clean(items),
        }
    )


@bp.get("/users/<user>/profile")
@require_auth("viewer")
def user_profile(user):
    engine, err = _engine_or_503()
    if err:
        return err

    rows = engine.user_days(user)
    if rows.empty:
        return jsonify({"error": f"no activity recorded for {user}"}), 404

    identity = get_directory().get(user, {})
    baseline = (
        engine.baselines.loc[user] if user in engine.baselines.index else None
    )
    baseline_view = []
    for feat in BEHAVIOURAL_COLUMNS:
        baseline_view.append(
            {
                "feature": feat,
                "label": FEATURE_LABELS.get(feat, feat),
                "baseline_mean": round(
                    float(baseline.get(f"{feat}_mean", 0.0)) if baseline is not None else 0.0, 2
                ),
                "baseline_std": round(
                    float(baseline.get(f"{feat}_std", 0.0)) if baseline is not None else 0.0, 2
                ),
                "observed_mean": round(float(rows[feat].mean()), 2),
                "observed_max": round(float(rows[feat].max()), 2),
                "population_mean": round(float(engine.pop_means.get(feat, 0.0)), 2),
            }
        )

    return jsonify(
        _clean(
            {
                "user": user,
                "identity": {
                    "name": identity.get("name", "Unknown"),
                    "role": identity.get("role", "Unknown"),
                    "department": identity.get("department", "Unknown"),
                    "team": identity.get("team", "Unknown"),
                },
                "peak_risk": round(float(rows["risk_score"].max()), 2),
                "mean_risk": round(float(rows["risk_score"].mean()), 2),
                "latest_risk": round(float(rows["risk_score"].iloc[-1]), 2),
                "severity": rows.loc[rows["risk_score"].idxmax(), "severity"],
                "active_days": int(len(rows)),
                "flagged_days": int((rows["risk_score"] >= Config.ALERT_THRESHOLD).sum()),
                "confirmed_days": int(rows["is_insider"].sum()),
                "baseline": baseline_view,
                "timeline": rows[["day_str", "risk_score", "ueba_score", "ml_probability", "severity"]]
                .rename(columns={"day_str": "day"})
                .round(3)
                .to_dict(orient="records"),
                "activity_totals": {
                    c: round(float(rows[c].sum()), 2) for c in BEHAVIOURAL_COLUMNS
                },
            }
        )
    )


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------
@bp.get("/alerts")
@require_auth("viewer")
def alerts():
    engine, err = _engine_or_503()
    if err:
        return err

    severity = request.args.get("severity")
    min_score = request.args.get("min_score", type=float)
    limit = min(int(request.args.get("limit", 100)), 500)

    rows = engine.alerts(min_score=min_score, severity=severity, limit=limit)
    directory = get_directory()
    leads = _lead_indicators(engine, rows)

    # Overlay analyst-managed case state.
    cases = {
        (c.subject_user, c.day): c
        for c in db.session.query(AlertCase).all()
    }

    items = []
    for pos, row in enumerate(rows.itertuples(index=False)):
        case = cases.get((row.user, row.day_str))
        items.append(
            {
                "user": row.user,
                "name": directory.get(row.user, {}).get("name", ""),
                "department": directory.get(row.user, {}).get("department", ""),
                "day": row.day_str,
                "risk_score": round(float(row.risk_score), 2),
                "ueba_score": round(float(row.ueba_score), 2),
                "ml_probability": round(float(row.ml_probability), 4),
                "severity": row.severity,
                "confirmed_insider": bool(row.is_insider),
                "status": case.status if case else "OPEN",
                "assigned_to": case.assigned_to if case else None,
                "top_indicator": leads[pos],
            }
        )
    return jsonify({"count": len(items), "threshold": Config.ALERT_THRESHOLD,
                    "items": _clean(items)})


def _lead_indicators(engine, rows) -> list[str]:
    """Headline indicator per alert row.

    Ranks by the same weighted, baseline-normalised deviation the risk score
    uses — not by raw counts. Raw counts would let a high-magnitude feature
    like files_copied_to_usb win every row regardless of how unusual it is.
    """
    if rows.empty:
        return []
    matrix, feats = ueba._weighted_matrix(rows, engine.baselines)
    weights = np.array([Config.RISK_WEIGHTS[f] for f in feats], dtype=float)
    winners = (matrix * weights).argmax(axis=1)
    return [FEATURE_LABELS.get(feats[i], feats[i]) for i in winners]


@bp.get("/alerts/cases")
@require_auth("viewer")
def list_cases():
    rows = db.session.query(AlertCase).order_by(AlertCase.updated_at.desc()).all()
    return jsonify({"count": len(rows), "items": [c.to_dict() for c in rows]})


@bp.post("/alerts/cases")
@require_auth("analyst")
def upsert_case():
    payload = request.get_json(silent=True) or {}
    user = (payload.get("user") or "").strip()
    day = (payload.get("day") or "").strip()
    status = (payload.get("status") or "OPEN").upper()

    if not user or not day:
        return jsonify({"error": "user and day are required"}), 400
    if status not in AlertCase.VALID_STATUSES:
        return jsonify({"error": "invalid status",
                        "allowed": list(AlertCase.VALID_STATUSES)}), 400

    engine, err = _engine_or_503()
    if err:
        return err
    row = engine.day_row(user, day)
    if row is None:
        return jsonify({"error": f"no activity for {user} on {day}"}), 404

    case = (
        db.session.query(AlertCase).filter_by(subject_user=user, day=day).first()
        or AlertCase(subject_user=user, day=day)
    )
    case.risk_score = float(row["risk_score"])
    case.severity = row["severity"]
    case.status = status
    case.assigned_to = payload.get("assigned_to") or current_username()
    if payload.get("notes") is not None:
        case.notes = payload["notes"]

    db.session.add(case)
    db.session.commit()
    record_audit(current_username(), "CASE_UPDATE", f"{user}/{day}", f"status={status}")
    return jsonify(case.to_dict())


# ---------------------------------------------------------------------------
# Investigation
# ---------------------------------------------------------------------------
@bp.get("/investigate/<user>")
@require_auth("analyst")
def investigate(user):
    engine, err = _engine_or_503()
    if err:
        return err

    day = request.args.get("day")
    result = engine.investigate(user, day)
    if not result:
        return jsonify({"error": f"no activity for {user}"
                                 + (f" on {day}" if day else "")}), 404

    result["identity"] = get_directory().get(user, {"name": "Unknown"})
    record_audit(current_username(), "INVESTIGATE", user, f"day={result['day']}")
    return jsonify(_clean(result))


@bp.post("/score")
@require_auth("analyst")
def score():
    """What-if scoring: submit a feature vector and get a risk verdict back."""
    engine, err = _engine_or_503()
    if err:
        return err

    payload = request.get_json(silent=True) or {}
    user = (payload.get("user") or "AD-HOC").strip()
    features = payload.get("features") or {
        k: v for k, v in payload.items() if k != "user"
    }
    if not isinstance(features, dict):
        return jsonify({"error": "features must be an object"}), 400

    unknown = set(features) - set(engine.feature_columns)
    if unknown:
        return jsonify({"error": "unknown features", "unknown": sorted(unknown),
                        "allowed": engine.feature_columns}), 400

    return jsonify(_clean(engine.score_record(user, features)))


@bp.get("/features")
@require_auth("viewer")
def features():
    engine, err = _engine_or_503()
    if err:
        return err
    return jsonify(
        {
            "feature_columns": engine.feature_columns,
            "labels": FEATURE_LABELS,
            "risk_weights": Config.RISK_WEIGHTS,
            "severity_thresholds": [
                {"min_score": s, "severity": n} for s, n in Config.SEVERITY_THRESHOLDS
            ],
        }
    )
