import json
import pickle
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
from pydantic import BaseModel

app = FastAPI(
    title="Insider Threat Detection API",
    description="Production-ready backend serving XGBoost predictions, Isolation Forest anomaly scores, and UEBA risk analytics.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
iso_forest = None
feature_cols = None
risk_config = None
demo_df = None

# Pre-computed evaluations cache on startup
evaluated_df = None
dashboard_summary = {}


def compute_behavioral_risk(row_dict: dict) -> float:
  weights = risk_config["component_weights"]
  norm = risk_config["normalization"]

  raw_vals = {
      "behavioral_anomalies_raw": row_dict.get("off_hours_logons", 0)
      + row_dict.get("off_hours_usb", 0),
      "privilege_misuse_raw": row_dict.get("usb_connects", 0)
      + row_dict.get("files_copied_to_usb", 0)
      + row_dict.get("sensitive_files_to_usb", 0),
      "data_access_violations_raw": row_dict.get("sensitive_files_to_usb", 0)
      + row_dict.get("external_emails_sent", 0)
      + row_dict.get("total_attachments", 0)
      + row_dict.get("total_email_size", 0),
      "access_pattern_deviations_raw": row_dict.get("distinct_pcs", 0)
      + row_dict.get("http_requests", 0)
      + row_dict.get("cloud_job_visits", 0),
      "historical_security_events_raw": row_dict.get(
          "historical_events_proxy", 0
      ),
  }

  score = 0.0
  mappings = [
      ("behavioral_anomalies_raw", "behavioral_anomalies"),
      ("privilege_misuse_raw", "privilege_misuse"),
      ("data_access_violations_raw", "data_access_violations"),
      ("access_pattern_deviations_raw", "access_pattern_deviations"),
      ("historical_security_events_raw", "historical_security_events"),
  ]

  for raw_key, weight_key in mappings:
    cap = norm.get(raw_key, {}).get("cap_p99", 1.0)
    norm_val = np.clip(raw_vals[raw_key], 0, cap) / cap
    score += norm_val * weights[weight_key]

  return float(np.clip(score * 100, 0, 100))


def map_severity(score: float) -> str:
  if score < 25:
    return "Low"
  elif score < 50:
    return "Medium"
  elif score < 75:
    return "High"
  else:
    return "Critical"


@app.on_event("startup")
def load_artifacts_and_evaluate():
  global model, iso_forest, feature_cols, risk_config, demo_df, evaluated_df, dashboard_summary
  try:
    with open("artifacts/final_model.pkl", "rb") as f:
      model = pickle.load(f)

    with open("artifacts/isolation_forest.pkl", "rb") as f:
      iso_forest = pickle.load(f)

    with open("artifacts/feature_columns.pkl", "rb") as f:
      feature_cols = pickle.load(f)

    with open("artifacts/risk_scoring_config.json", "r") as f:
      risk_config = json.load(f)

    demo_df = pd.read_csv("data/app_demo_data.csv")

    # Batch evaluate all dataset records
    feature_matrix = demo_df[feature_cols]
    ml_probs = model.predict_proba(feature_matrix)[:, 1] * 100
    iso_scores = -iso_forest.score_samples(feature_matrix)

    beh_scores = [
        compute_behavioral_risk(row)
        for row in demo_df.to_dict(orient="records")
    ]
    overall_scores = 0.5 * ml_probs + 0.5 * np.array(beh_scores)
    severities = [map_severity(s) for s in overall_scores]

    eval_df = demo_df.copy()
    eval_df["ml_probability"] = np.round(ml_probs, 2)
    eval_df["anomaly_score"] = np.round(iso_scores, 4)
    eval_df["behavioral_risk_score"] = np.round(beh_scores, 2)
    eval_df["overall_risk_score"] = np.round(overall_scores, 2)
    eval_df["severity"] = severities

    severity_order = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
    eval_df["severity_rank"] = eval_df["severity"].map(severity_order)
    eval_df = eval_df.sort_values(
        by=["severity_rank", "overall_risk_score"], ascending=[True, False]
    )

    evaluated_df = eval_df

    # Aggregate by week for smooth trend curve
    eval_df["date_dt"] = pd.to_datetime(eval_df["day"])
    trend_df = (
        eval_df.groupby(pd.Grouper(key="date_dt", freq="W"))[
            "overall_risk_score"
        ]
        .mean()
        .round(2)
        .reset_index()
    )
    trend_df = trend_df.dropna()

    trend_records = [
        {
            "session": row["date_dt"].strftime("%Y-%m-%d"),
            "risk": row["overall_risk_score"],
        }
        for _, row in trend_df.iterrows()
    ]

    counts = eval_df["severity"].value_counts().to_dict()
    dashboard_summary = {
        "total_users": int(eval_df["user"].nunique()),
        "total_sessions": int(len(eval_df)),
        "avg_risk": round(float(eval_df["overall_risk_score"].mean()), 1),
        "high_count": int(counts.get("High", 0)),
        "critical_count": int(counts.get("Critical", 0)),
        "severity_distribution": {
            "Low": int(counts.get("Low", 0)),
            "Medium": int(counts.get("Medium", 0)),
            "High": int(counts.get("High", 0)),
            "Critical": int(counts.get("Critical", 0)),
        },
        "trend": trend_records,
        "top_targets": eval_df.head(10).to_dict(orient="records"),
    }
    print(
        f"✅ Full Dataset Evaluated: {len(eval_df)} sessions across"
        f" {eval_df['user'].nunique()} identities"
    )
  except Exception as e:
    print(f"❌ Error loading artifacts or pre-evaluating: {e}")


class UserActivityPayload(BaseModel):
  user: str
  day: str
  logon_count: int
  off_hours_logons: int
  distinct_pcs: int
  usb_connects: float
  off_hours_usb: float
  files_copied_to_usb: float
  sensitive_files_to_usb: float
  total_emails_sent: float
  external_emails_sent: float
  total_attachments: float
  total_email_size: float
  http_requests: float
  cloud_job_visits: float
  role_encoded: int
  department_encoded: int
  supervisor_encoded: int
  historical_events_proxy: Optional[float] = 0.0


@app.get("/")
def root():
  return {
      "status": "Online",
      "system": "Insider Threat Detection API",
      "docs_url": "/docs",
  }


@app.get("/api/dashboard/stats")
def get_dashboard_stats():
  if not dashboard_summary:
    raise HTTPException(
        status_code=500, detail="Dashboard stats not initialized"
    )
  return dashboard_summary


@app.get("/api/feed")
def get_replay_feed(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    severity: Optional[str] = "All",
):
  if evaluated_df is None:
    raise HTTPException(
        status_code=500, detail="Evaluated dataset not available"
    )

  filtered = evaluated_df
  if severity and severity != "All":
    filtered = filtered[filtered["severity"] == severity]

  total_matching = len(filtered)
  start_idx = (page - 1) * limit
  records = filtered.iloc[start_idx : start_idx + limit].to_dict(
      orient="records"
  )

  return {
      "total": total_matching,
      "page": page,
      "limit": limit,
      "records": records,
  }


@app.get("/api/users")
def get_users():
  if demo_df is None:
    raise HTTPException(status_code=500, detail="Demo dataset not loaded")
  users = sorted(demo_df["user"].unique().tolist())
  return {"total_users": len(users), "users": users}


@app.get("/api/users/{user_id}/logs")
def get_user_logs(user_id: str):
  if evaluated_df is None:
    raise HTTPException(status_code=500, detail="Dataset not loaded")
  user_records = evaluated_df[evaluated_df["user"] == user_id]
  if user_records.empty:
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
  return {
      "user": user_id,
      "total_records": len(user_records),
      "records": user_records.to_dict(orient="records"),
  }


@app.post("/api/predict")
def predict_threat(payload: UserActivityPayload):
  input_dict = payload.dict()
  input_df = pd.DataFrame([input_dict])[feature_cols]

  ml_prob = float(model.predict_proba(input_df)[:, 1][0]) * 100
  iso_raw = -float(iso_forest.score_samples(input_df)[0])
  beh_score = compute_behavioral_risk(input_dict)
  overall_score = 0.5 * ml_prob + 0.5 * beh_score
  severity = map_severity(overall_score)

  return {
      "user": payload.user,
      "day": payload.day,
      "ml_probability": round(ml_prob, 2),
      "anomaly_score": round(iso_raw, 4),
      "behavioral_risk_score": round(beh_score, 2),
      "overall_risk_score": round(overall_score, 2),
      "severity": severity,
  }