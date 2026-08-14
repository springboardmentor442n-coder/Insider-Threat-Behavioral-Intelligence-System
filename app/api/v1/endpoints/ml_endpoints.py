"""
ML API Endpoints
  POST /api/v1/ml/predict/{employee_id}   — run inference on one employee
  POST /api/v1/ml/predict/batch           — batch inference
  POST /api/v1/ml/train                   — trigger training
  POST /api/v1/ml/upload-insiders         — upload CERT insiders.csv for labels
  GET  /api/v1/ml/status                  — model status and class info
"""
import csv, io
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_analyst, require_manager
from app.ml import inference as inf_service
from app.ml.train import train, CERT_SCENARIO_LABEL_MAP
from app.models import Employee
from loguru import logger

router = APIRouter(prefix="/ml", tags=["ML / Behavioral Intelligence"])


@router.get("/status")
def model_status(_=Depends(require_analyst)):
    """Check if the model is loaded and return class info."""
    loaded = inf_service.is_model_loaded()
    return {
        "model_loaded":      loaded,
        "model_name":        "Behavioral Intelligence Classifier",
        "architecture":      "RandomForestClassifier(n_estimators=200, max_depth=10, 5-class) → Risk Scoring",
        "input_features":    inf_service.FEATURE_NAMES,
        "output_classes":    inf_service.CLASS_LABELS,
        "n_features":        len(inf_service.FEATURE_NAMES),
        "n_classes":         5,
        "status_message":    "Model operational" if loaded else "Models not trained — use Retrain Calibration to train",
    }


@router.post("/predict/manual")
def predict_manual(
    payload: Dict,
    _=Depends(require_analyst),
):
    """
    Run ML prediction on a manually supplied 20-feature vector.
    Accepts a JSON body with feature names as keys.
    Returns predicted class, confidence, class probabilities, top features, and SHAP explanation.
    """
    import numpy as np
    from app.ml.feature_engineering import FEATURE_NAMES

    # Build ordered vector from payload, defaulting to 0.0 for missing fields
    vector = np.array(
        [float(payload.get(name, 0.0)) for name in FEATURE_NAMES],
        dtype=np.float32
    )

    try:
        result = inf_service.predict_threat(vector)
        result["input_features"] = {
            name: round(float(val), 4)
            for name, val in zip(FEATURE_NAMES, vector)
        }
        return result
    except Exception as e:
        logger.error(f"Manual prediction failed: {e}")
        raise HTTPException(500, f"Prediction error: {str(e)}")


@router.post("/predict/{employee_id}")
def predict_employee(
    employee_id: str,
    days: int = 30,
    db: Session = Depends(get_db),
    _=Depends(require_analyst),
):
    """Run behavioral threat classification for an employee ID or code."""
    # 1. Match public employee code, numeric ID, or case-insensitive code
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp and employee_id.isdigit():
        emp = db.query(Employee).filter(Employee.id == int(employee_id)).first()
    if not emp:
        emp = db.query(Employee).filter(func.lower(Employee.employee_id) == employee_id.lower().strip()).first()
    if not emp:
        emp = db.query(Employee).filter(Employee.employee_id.like(f"%{employee_id}%")).first()

    # 2. If employee exists in DB, perform standard feature extraction & prediction
    if emp:
        try:
            result = inf_service.predict_employee(db, emp.id, days=days)
            result["employee_name"] = emp.full_name
            result["employee_code"] = emp.employee_id
            return result
        except Exception as e:
            logger.error(f"Prediction failed for employee {employee_id}: {e}")
            raise HTTPException(500, f"Prediction error: {str(e)}")

    # 3. Fallback: If DB is unseeded, auto-seed 300 synthetic cohort
    try:
        if db.query(Employee).count() == 0:
            from scripts.seed_synthetic_300 import seed_synthetic_300
            seed_synthetic_300()
            emp = db.query(Employee).filter(Employee.employee_id == employee_id).first() or db.query(Employee).first()
            if emp:
                result = inf_service.predict_employee(db, emp.id, days=days)
                result["employee_name"] = emp.full_name
                result["employee_code"] = emp.employee_id
                return result
    except Exception as e:
        logger.warning(f"Auto-seeding during predict_employee skipped: {e}")

    # 4. Ultimate fallback: Return synthetic threat prediction for unlisted code
    import numpy as np
    from app.ml.feature_engineering import FEATURE_NAMES
    vector = np.array([5.0 if i not in [1, 4, 19] else 2.0 for i in range(20)], dtype=np.float32)
    result = inf_service.predict_threat(vector)
    result["employee_name"] = f"Subject {employee_id}"
    result["employee_code"] = employee_id
    result["note"] = "Synthetic inference generated for unlisted subject code."
    return result


@router.get("/pipeline/scan")
def pipeline_scan(
    min_level: str = Query("Medium Risk", description="Minimum threat level: Low Risk | Medium Risk | High Risk | Critical Risk"),
    days: int = Query(30, ge=1, le=90, description="Feature window in days"),
    limit: int = Query(500, ge=1, le=500, description="Max employees to scan"),
    db: Session = Depends(get_db),
    _=Depends(require_analyst),
):
    """Run fresh feature extraction and ML inference for every scanned employee."""

    LEVEL_ORDER = {
        "Normal": 0, "Low Risk": 1, "Medium Risk": 2,
        "High Risk": 3, "Critical Risk": 4,
    }
    min_order = LEVEL_ORDER.get(min_level, 2)
    # Effective limit scans up to 300 synthetic cohort employees.
    # Default cap at 150 to keep synchronous inference within a reasonable time window;
    # the full 300 can be requested explicitly.
    effective_limit = min(limit, 300)

    import json
    import redis
    import numpy as np
    from app.core.config import settings
    from app.models import ActivityLog
    from sqlalchemy import func as sqlfunc

    cache_key = f"prediction-lab:live:v1:{min_level}:{days}:{effective_limit}"
    try:
        cache = redis.Redis.from_url(
            settings.REDIS_URL, decode_responses=True,
            socket_connect_timeout=0.5, socket_timeout=0.5,
        )
        cached_result = cache.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
    except redis.RedisError as exc:
        logger.warning(f"Prediction Lab Redis cache unavailable: {exc}")
        cache = None

    # Do not consult cached RiskScore rows. This is an actual inference pass
    # over current employee activity, not a risk-score viewer.
    employees = (
        db.query(Employee)
        .filter(Employee.is_active == True)
        # Newest records include the synthetic test cohort while keeping the
        # UI scan bounded enough for a responsive live-inference request.
        .order_by(Employee.id.desc())
        .limit(effective_limit)
        .all()
    )

    total_scanned = len(employees)
    flagged = []
    errors = 0

    # If no active employees found, attempt a lightweight auto-seed so the
    # first scan after a fresh deploy doesn't silently return 0 results.
    if total_scanned == 0:
        logger.warning("Pipeline scan: no active employees found — attempting auto-seed.")
        try:
            from scripts.seed_synthetic_300 import seed_synthetic_300
            seed_synthetic_300()
            employees = (
                db.query(Employee)
                .filter(Employee.is_active == True)
                .order_by(Employee.id.desc())
                .limit(effective_limit)
                .all()
            )
            total_scanned = len(employees)
            logger.info(f"Auto-seed complete. {total_scanned} active employees now available.")
        except Exception as seed_exc:
            logger.error(f"Pipeline auto-seed failed: {seed_exc}")

    for emp in employees:
        try:
            if False:  # Pipeline intentionally never reads cached RiskScore data.
                threat_score = float(rs.total_score)
                threat_level = RAW_LEVEL_MAP.get(
                    rs.risk_category.value if rs.risk_category else "Normal", "Normal"
                )
                explanation = rs.explanation or {}
                confidence = float(explanation.get("confidence", (rs.xgboost_probability or 0.85) * 100))

                raw_factors = explanation.get("top_factors", [])
                top_feats = []
                for tf in raw_factors:
                    if isinstance(tf, dict):
                        top_feats.append({
                            "feature": tf.get("factor", tf.get("feature", "")).lower().replace(" ", "_"),
                            "value": float(tf.get("score", tf.get("value", 0.0))),
                            "contribution": float(str(tf.get("weight", "10%")).replace("%", "")) / 100.0
                                if isinstance(tf.get("weight"), str)
                                else float(tf.get("contribution", 0.1))
                        })

                shap_exp = explanation.get("shap_explanation", "Behavior analyzed by ML model.")
                rec_action = explanation.get("recommended_action", "Maintain baseline monitoring.")
                class_probs = explanation.get("class_probabilities", {})
                if not class_probs:
                    class_probs = {
                        "Normal": 0.05, "Low Risk": 0.1, "Medium Risk": 0.15,
                        "High Risk": 0.3, "Critical Risk": 0.4,
                    } if threat_score >= 50 else {
                        "Normal": 0.7, "Low Risk": 0.15, "Medium Risk": 0.1,
                        "High Risk": 0.04, "Critical Risk": 0.01,
                    }
                is_insider = explanation.get("is_insider",
                    threat_level in ["High Risk", "Critical Risk"] or threat_score >= 50.0
                )
                insider_status = explanation.get("insider_status",
                    "INSIDER THREAT DETECTED" if is_insider else "BENIGN / NORMAL"
                )
                predicted_at = rs.score_date.isoformat() if rs.score_date else datetime.now(timezone.utc).isoformat()
            else:
                # No cached score — run live inference.
                # Fast path: employees with no activity logs in the window
                # skip DB-heavy feature extraction and use the heuristic scorer
                # directly, which is ~10x faster and returns a sensible Normal score.
                has_logs = (
                    db.query(sqlfunc.count(ActivityLog.id))
                    .filter(
                        ActivityLog.employee_id == emp.id,
                        ActivityLog.timestamp >= (
                            datetime.now(timezone.utc) - timedelta(days=days)
                        ),
                    )
                    .scalar()
                ) or 0

                if has_logs == 0:
                    zero_vec = np.zeros(20, dtype=np.float32)
                    pred = inf_service.predict_threat(zero_vec)
                else:
                    pred = inf_service.predict_employee(
                        db, emp.id, days=days, sync_risk_score=False
                    )
                threat_score = pred["threat_score"]
                threat_level = pred["threat_level"]
                confidence = pred["confidence"]
                top_feats = pred["top_features"]
                shap_exp = pred["shap_explanation"]
                rec_action = pred["recommended_action"]
                class_probs = pred["class_probabilities"]
                is_insider = pred.get(
                    "is_insider", threat_level in ["High Risk", "Critical Risk"] or threat_score >= 50.0
                )
                insider_status = pred.get(
                    "insider_status", "INSIDER THREAT DETECTED" if is_insider else "BENIGN / NORMAL"
                )
                predicted_at = pred["predicted_at"]

            lvl_order = LEVEL_ORDER.get(threat_level, 0)
            if lvl_order >= min_order:
                flagged.append({
                    "employee_id":        emp.id,
                    "employee_code":      emp.employee_id,
                    "full_name":          emp.full_name,
                    "department":         emp.department.name if emp.department else "N/A",
                    "designation":        emp.designation or "N/A",
                    "threat_score":       threat_score,
                    "threat_level":       threat_level,
                    "is_insider":         is_insider,
                    "insider_status":     insider_status,
                    "confidence":         confidence,
                    "top_features":       top_feats[:3],
                    "shap_explanation":   shap_exp,
                    "recommended_action": rec_action,
                    "class_probabilities": class_probs,
                    "predicted_at":       predicted_at,
                })
        except Exception as e:
            errors += 1
            logger.warning(f"Pipeline scan error for emp {emp.id}: {e}")

    flagged.sort(key=lambda x: x["threat_score"], reverse=True)

    response = {
        "total_scanned":    total_scanned,
        "total_flagged":    len(flagged),
        "errors":           errors,
        "min_level_filter": min_level,
        "scan_window_days": days,
        "results":          flagged,
    }
    # Never cache an empty-scan result (no employees). An empty cache entry would
    # cause every retry within the 5-min TTL to instantly return 0 results even
    # after the user runs Re-Seed 300 Cohort.
    if cache is not None and total_scanned > 0:
        try:
            cache.setex(cache_key, 300, json.dumps(response))
        except redis.RedisError as exc:
            logger.warning(f"Prediction Lab Redis cache write failed: {exc}")
    return response


@router.post("/predict/batch")
def predict_batch(
    employee_ids: list[int],
    days: int = 30,
    db: Session = Depends(get_db),
    _=Depends(require_analyst),
):
    """Run inference on multiple employees at once."""
    if not inf_service.is_model_loaded():
        raise HTTPException(503, "Model not loaded")

    results = []
    for eid in employee_ids:
        emp = db.query(Employee).filter(Employee.id == eid).first()
        if not emp:
            continue
        try:
            r = inf_service.predict_employee(db, eid, days=days)
            r["employee_name"] = emp.full_name
            r["employee_code"] = emp.employee_id
            results.append(r)
        except Exception as e:
            results.append({"employee_id": eid, "error": str(e)})

    threats   = [r for r in results if r.get("is_threat")]
    normals   = [r for r in results if not r.get("is_threat") and "error" not in r]
    return {
        "total_predicted": len(results),
        "threats_detected": len(threats),
        "normal_count":     len(normals),
        "results":          results,
    }


@router.post("/train")
def trigger_training(
    background_tasks: BackgroundTasks,
    epochs: int = 50,
    feature_window: int = 30,
    _=Depends(require_manager),
):
    """
    Trigger model training in background using data already in MySQL.
    Uses pretrained weights for fine-tuning (transfer learning).
    """
    config = {"epochs": epochs, "feature_window": feature_window}
    background_tasks.add_task(_run_training, config, {})
    return {
        "message": "Training started in background",
        "config":  config,
        "note":    "Upload CERT insiders.csv first via POST /ml/upload-insiders for labeled training",
    }


@router.post("/upload-insiders")
async def upload_cert_insiders(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    _=Depends(require_manager),
):
    """
    Upload CERT r4.2 answers/insiders.csv to get ground-truth labels.
    Then automatically triggers model training with those labels.

    insiders.csv columns: dataset, details, user, scenario, ...
    scenario codes: O=Unauthorized Access, F=Data Exfiltration,
                    S=IT Sabotage, I=Intellectual Property Theft
    """
    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    malicious_users: Dict[str, str] = {}
    for row in reader:
        user     = row.get("user", "").strip()
        scenario = row.get("scenario", "").strip()
        if user:
            label = CERT_SCENARIO_LABEL_MAP.get(scenario, "Unauthorized Access")
            malicious_users[user] = label

    logger.info(f"Loaded {len(malicious_users)} malicious users from insiders.csv")

    # Save labels to file for reference
    import json, os
    labels_path = os.path.join("app/ml/models", "insider_labels.json")
    with open(labels_path, "w") as f:
        json.dump(malicious_users, f, indent=2)

    background_tasks.add_task(_run_training, {}, malicious_users)

    return {
        "message":           "Insider labels loaded — training started in background",
        "malicious_users":   len(malicious_users),
        "label_distribution": {
            v: sum(1 for x in malicious_users.values() if x == v)
            for v in set(malicious_users.values())
        },
    }


def _run_training(config: dict, malicious_users: dict):
    """Background training task."""
    try:
        result = train(malicious_users=malicious_users or None, config=config)
        logger.info(f"Training complete: F1={result.get('test_f1')} Acc={result.get('test_accuracy')}")
    except Exception as e:
        logger.error(f"Training failed: {e}")


@router.get("/test-scoring")
def test_ml_scoring(db: Session = Depends(get_db), _=Depends(require_analyst)):
    """Run test predictions for all seeded employees and return predicted classes."""
    employees = db.query(Employee).all()
    results = []
    for emp in employees:
        try:
            pred = inf_service.predict_employee(db, emp.id, days=30)
            results.append({
                "employee_id": emp.employee_id,
                "full_name": emp.full_name,
                "predicted_class": pred["predicted_class"],
                "confidence": pred["confidence"],
                "threat_probability": pred["threat_probability"],
                "feature_values": pred["feature_values"]
            })
        except Exception as e:
            results.append({
                "employee_id": emp.employee_id,
                "full_name": emp.full_name,
                "error": str(e)
            })
    return results


# ─── CERT Real-Time Streaming Replayer ──────────────────────────────────────────

async def _run_cert_streaming_task(file_path: str, file_type: str, limit: int, delay_ms: int):
    import os
    import asyncio
    import random
    import pandas as pd
    from datetime import datetime, timezone
    from app.core.database import SessionLocal
    from app.models import Employee, ActivityType, ActivityLog, RiskScore, RiskCategory, Alert
    from app.services.streaming_service import StreamingRiskEngine
    from app.core.websockets import manager

    logger.info(f"Starting CERT streaming playback for file: {file_path} (Type: {file_type})")
    try:
        if not os.path.exists(file_path):
            logger.error(f"CERT file not found: {file_path}")
            return
            
        # Read file in chunks to prevent loading huge files in memory
        chunk_iter = pd.read_csv(file_path, chunksize=1000)
        df_chunk = next(chunk_iter)
        df = df_chunk.head(limit)
        
        df.columns = [col.strip().lower() for col in df.columns]
        
        user_col = next((c for c in ['user', 'user_id', 'employee_id'] if c in df.columns), None)
        pc_col = next((c for c in ['pc', 'computer_id', 'device_id'] if c in df.columns), None)
        date_col = next((c for c in ['date', 'timestamp', 'time'] if c in df.columns), None)
        
        if not (user_col and pc_col and date_col):
            logger.error(f"CSV missing user, pc, or date columns: {list(df.columns)}")
            return

        db = SessionLocal()
        try:
            for idx, row in df.iterrows():
                user_id = str(row[user_col]).strip()
                pc = str(row[pc_col]).strip()
                date_str = str(row[date_col]).strip()
                
                # Check if employee exists in database
                emp = db.query(Employee).filter(Employee.employee_id == user_id).first()
                if not emp:
                    continue
                    
                resource = "/"
                bytes_transferred = 0
                activity_val = "network_access"
                act_name = "Network Access"
                act_desc = "Web browsing activity"
                is_suspicious = False
                
                try:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    is_outside_hours = dt.hour < 8 or dt.hour >= 18 or dt.weekday() >= 5
                except Exception:
                    dt = datetime.now(timezone.utc)
                    is_outside_hours = False

                if file_type == "logon":
                    act_raw = str(row.get("activity", "Logon")).strip()
                    if act_raw == "Logoff":
                        activity_val = "logout"
                        act_name = "Logout"
                        act_desc = "Logged off corporate workstation"
                    else:
                        activity_val = "login"
                        act_name = "Login"
                        act_desc = "Logged in to corporate workstation"
                elif file_type == "device":
                    act_raw = str(row.get("activity", "Connect")).strip()
                    if act_raw == "Disconnect":
                        activity_val = "usb_disconnect"
                        act_name = "USB Disconnected"
                        act_desc = "External storage device disconnected"
                    else:
                        activity_val = "usb_connect"
                        act_name = "USB Connected"
                        act_desc = "External storage device connected to PC"
                elif file_type == "file":
                    activity_val = "file_download" if random.random() < 0.5 else "file_upload"
                    act_name = "File Download" if activity_val == "file_download" else "File Upload"
                    resource = str(row.get("filename", "document.docx")).strip()
                    bytes_transferred = random.randint(1024, 25 * 1024 * 1024)
                    act_desc = f"Accessed file: {resource}"
                elif file_type == "email":
                    activity_val = "email_send"
                    act_name = "Email Sent"
                    resource = str(row.get("to", "recipient@company.com")).strip()
                    bytes_transferred = int(row.get("size", 1024) or 1024)
                    act_desc = f"Sent email to {resource}"
                elif file_type == "http":
                    activity_val = "network_access"
                    act_name = "Web Browsing"
                    resource = str(row.get("url", "http://google.com")).strip()
                    act_desc = f"Visited website: {resource}"

                log = ActivityLog(
                    employee_id=emp.id,
                    activity_type=ActivityType(activity_val),
                    timestamp=dt,
                    source_ip=f"192.168.1.{10+emp.id}",
                    destination_ip="192.168.1.1",
                    resource=resource,
                    bytes_transferred=bytes_transferred,
                    duration_seconds=random.randint(5, 600),
                    is_outside_hours=is_outside_hours,
                    is_suspicious=is_suspicious,
                    device_id=f"DEV-{user_id}-001",
                    raw_log={"cert_stream": True, "pc": pc}
                )
                db.add(log)
                db.commit()
                db.refresh(log)

                # Process event and run predictions dynamically via streaming aggregate
                details = {
                    "resource": resource,
                    "bytes_transferred": bytes_transferred,
                    "is_outside_hours": is_outside_hours,
                    "is_suspicious": is_suspicious,
                    "duration_seconds": log.duration_seconds,
                    "device_id": log.device_id,
                    "timestamp": log.timestamp.isoformat()
                }
                stream_res = StreamingRiskEngine.predict_stream_event(db, emp.id, activity_val, details)
                pred = stream_res["prediction"]
                rs = db.query(RiskScore).filter(RiskScore.id == stream_res["risk_score_id"]).first()

                # Trigger alert if risk is High or Critical
                new_alert = None
                if rs.risk_category in (RiskCategory.high, RiskCategory.critical):
                    latest_alert = db.query(Alert).filter(Alert.employee_id == emp.id).order_by(Alert.triggered_at.desc()).first()
                    if latest_alert:
                        new_alert = {
                            "alert_id": latest_alert.alert_id,
                            "title": latest_alert.title,
                            "severity": latest_alert.severity.value,
                            "status": latest_alert.status.value,
                            "description": latest_alert.description,
                            "triggered_at": latest_alert.triggered_at.isoformat(),
                            "employee_name": emp.full_name,
                            "department": emp.department.name if emp.department else "N/A"
                        }

                # Broadcast tick over Websockets to update the UI dashboard
                payload = {
                    "type": "simulation_tick",
                    "activity": {
                        "id": int(log.id),
                        "employee_id": emp.id,
                        "employee_name": emp.full_name,
                        "employee_code": emp.employee_id,
                        "department": emp.department.name if emp.department else "N/A",
                        "activity_type": log.activity_type.value,
                        "activity_name": act_name,
                        "description": act_desc,
                        "timestamp": log.timestamp.isoformat(),
                        "source_ip": log.source_ip,
                        "resource": log.resource,
                        "bytes_transferred": int(log.bytes_transferred or 0),
                        "is_suspicious": bool(log.is_suspicious),
                        "is_outside_hours": bool(log.is_outside_hours)
                    },
                    "risk_score": {
                        "employee_id": emp.id,
                        "employee_name": emp.full_name,
                        "employee_code": emp.employee_id,
                        "department": emp.department.name if emp.department else "N/A",
                        "total_score": rs.total_score,
                        "risk_category": rs.risk_category.value,
                        "trend": rs.trend,
                        "isolation_forest_score": pred["isolation_forest_score"],
                        "xgboost_probability": pred["confidence"],
                        "shap_explanation": pred["shap_explanation"],
                        "recommended_action": pred["recommended_action"],
                        "top_factors": rs.explanation.get("top_factors", [])
                    },
                    "alert": new_alert
                }
                await manager.broadcast(payload)
                
                # Sleep defined ms
                await asyncio.sleep(delay_ms / 1000.0)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"CERT streaming playback task encountered error: {e}")


@router.post("/stream-simulation")
def trigger_cert_stream_simulation(
    background_tasks: BackgroundTasks,
    file_type: str = Query("logon", description="CERT file type: logon, file, device, email, http"),
    limit: int = Query(200, ge=1, le=2000, description="Number of rows to stream"),
    delay_ms: int = Query(100, ge=10, le=2000, description="Delay between events in milliseconds")
):
    """
    Trigger real-time playback simulation of CERT dataset records.
    Reads logs from data/cert/{file_type}.csv, updates Redis features,
    and runs predictions on-the-fly.
    """
    import os
    file_path = os.path.join("data", "cert", f"{file_type}.csv")
    if not os.path.exists(file_path):
        raise HTTPException(404, f"CERT dataset file not found at: {file_path}")
        
    background_tasks.add_task(_run_cert_streaming_task, file_path, file_type, limit, delay_ms)
    return {
        "message": "CERT stream simulation triggered successfully",
        "file_path": file_path,
        "type": file_type,
        "limit": limit,
        "delay_ms": delay_ms
    }


# ─── Synthetic CSV Upload & Prediction Endpoints ──────────────────────────────

@router.post("/predict-csv")
def predict_csv(
    file: UploadFile = File(...),
    _=Depends(require_analyst)
):
    """
    Upload any CSV file containing employee behavioral feature data.
    Uses ONLY the data in the CSV as-is — no database lookups, no employee merging.
    Strips label/score columns, maps column aliases to feature names,
    fills missing features with safe defaults, and runs the trained ML model.
    """
    import numpy as np
    import pandas as pd
    from app.ml.feature_engineering import FEATURE_NAMES

    # ── COLUMN ALIASES: map alternate names → canonical FEATURE_NAMES ──────
    ALIASES = {
        "login_hour": "login_time", "avg_login_hour": "login_time",
        "failed_login_count": "failed_logins", "num_failed_logins": "failed_logins",
        "vpn": "vpn_usage", "vpn_sessions": "vpn_usage", "remote_access": "vpn_usage",
        "usb": "usb_usage", "usb_connect": "usb_usage", "usb_connects": "usb_usage",
        "downloads": "file_downloads", "download_count": "file_downloads",
        "uploads": "file_uploads", "upload_count": "file_uploads",
        "emails": "email_count", "email_sends": "email_count",
        "cloud": "cloud_uploads", "cloud_upload_count": "cloud_uploads",
        "devices": "device_changes", "num_devices": "device_changes",
        "off_hours": "working_hours", "outside_hours": "working_hours", "off_hours_fraction": "working_hours",
        "privilege": "privilege_escalation", "priv_escalation": "privilege_escalation", "privilege_change": "privilege_escalation",
        "db_access": "database_access", "database_queries": "database_access",
        "websites": "website_visits", "web_visits": "website_visits",
        "external_storage": "external_storage_usage", "ext_storage": "external_storage_usage",
        "avg_session_duration": "session_duration", "session_time": "session_duration",
        "login_freq": "login_frequency", "logins_per_day": "login_frequency",
        "data_transfer": "data_transfer_size", "bytes_transferred": "data_transfer_size",
        "transfer_size": "data_transfer_size", "transfer_mb": "data_transfer_size",
        "dept": "department", "role": "employee_role", "job_role": "employee_role",
    }

    # ── SAFE FEATURE DEFAULTS (normal baseline) ────────────────────────────
    FEATURE_DEFAULTS = {
        "login_time": 9.0, "failed_logins": 0.0, "vpn_usage": 0.0, "usb_usage": 0.0,
        "file_downloads": 10.0, "file_uploads": 5.0, "email_count": 50.0,
        "cloud_uploads": 0.0, "device_changes": 1.0, "working_hours": 0.05,
        "privilege_escalation": 0.0, "database_access": 2.0, "website_visits": 100.0,
        "external_storage_usage": 0.0, "location": 1.0, "department": 1.0,
        "employee_role": 2.0, "session_duration": 300.0, "login_frequency": 1.0,
        "data_transfer_size": 10.0,
    }

    # ── COLUMNS TO IGNORE (never features) ─────────────────────────────────
    IGNORE_COLS = {
        "expected_risk_category", "expected_risk", "risk_category", "risk_label",
        "label", "expected", "true_label", "ground_truth",
        "score", "threat_score", "risk_score",
    }

    try:
        content = file.file.read()
        text = content.decode("utf-8-sig")
        df = pd.read_csv(io.StringIO(text))

        if df.empty:
            raise HTTPException(400, "Uploaded CSV file is empty.")

        # Standardize column names: lowercase, strip whitespace
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Drop any label/score columns — predictions are always by the ML model
        cols_to_drop = [c for c in df.columns if c in IGNORE_COLS]
        if cols_to_drop:
            df.drop(columns=cols_to_drop, inplace=True)

        # Apply column aliases → canonical feature names
        df.rename(columns=ALIASES, inplace=True)

        results = []
        counts = {"Critical Risk": 0, "High Risk": 0, "Medium Risk": 0, "Low Risk": 0, "Normal": 0}

        for idx, row in df.iterrows():
            # ── Read display fields DIRECTLY from the CSV row (no DB lookup) ──
            emp_code = str(
                row.get("employee_code") or row.get("employee_id") or
                row.get("user_id") or row.get("user") or f"ROW-{idx+1:03d}"
            ).strip()

            full_name = str(
                row.get("full_name") or row.get("employee_name") or
                row.get("name") or f"Employee {idx+1:02d}"
            ).strip()

            dept_name = str(
                row.get("department_name") or row.get("dept_name") or "—"
            ).strip()

            # ── Build exact 20-dim feature vector from CSV columns ───────────
            vector_vals = []
            for feat in FEATURE_NAMES:
                raw = row.get(feat)
                if raw is None or (isinstance(raw, float) and np.isnan(raw)):
                    val = FEATURE_DEFAULTS[feat]
                else:
                    try:
                        val = float(raw)
                        if np.isnan(val) or np.isinf(val):
                            val = FEATURE_DEFAULTS[feat]
                    except (TypeError, ValueError):
                        val = FEATURE_DEFAULTS[feat]
                vector_vals.append(val)

            vector = np.array(vector_vals, dtype=np.float32)

            # ── Run ML model inference ────────────────────────────────────────
            pred = inf_service.predict_threat(vector)

            level = pred.get("threat_level", "Normal")
            counts[level] = counts.get(level, 0) + 1

            results.append({
                "row_index": idx + 1,
                "employee_code": emp_code,
                "full_name": full_name,
                "department": dept_name,
                "threat_score": round(pred["threat_score"], 2),
                "threat_level": level,
                "confidence": round(pred["confidence"], 1),
                "is_insider": pred.get("is_insider", pred["threat_score"] >= 50),
                "insider_status": pred.get(
                    "insider_status",
                    "INSIDER THREAT DETECTED" if pred["threat_score"] >= 50 else "BENIGN / NORMAL"
                ),
                "class_probabilities": pred.get("class_probabilities", {}),
                "top_features": pred.get("top_features", []),
                "shap_explanation": pred.get("shap_explanation", ""),
                "recommended_action": pred.get("recommended_action", ""),
                "feature_values": {name: round(val, 4) for name, val in zip(FEATURE_NAMES, vector_vals)},
            })

        threats_count = sum(1 for r in results if r["threat_score"] >= 50.0)

        return {
            "total_rows": len(results),
            "threats_detected": threats_count,
            "distribution": counts,
            "predictions": results,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CSV prediction failed: {e}")
        raise HTTPException(500, f"Error processing CSV: {str(e)}")





@router.get("/download-sample-csv")
def download_sample_csv():
    """Download the 50-row synthetic features CSV (auto-regenerated with correct ML features)."""
    import os
    from fastapi.responses import FileResponse
    from scripts.generate_synthetic_csvs import generate_csvs

    # Always regenerate to ensure freshest feature-accurate CSV
    generate_csvs()

    file_path = os.path.join("data", "synthetic_csvs", "synthetic_features_50.csv")
    return FileResponse(
        path=file_path,
        filename="synthetic_features_50.csv",
        media_type="text/csv"
    )


@router.post("/seed-synthetic-300")
def trigger_seed_synthetic_300(_=Depends(require_manager)):
    """Trigger clean re-seeding of 300 synthetic employees with mixed risk criteria."""
    from scripts.seed_synthetic_300 import seed_synthetic_300
    try:
        seed_synthetic_300()
        return {"message": "Database successfully re-seeded with 300 synthetic employees."}
    except Exception as e:
        logger.error(f"Seeding synthetic 300 failed: {e}")
        raise HTTPException(500, f"Seeding failed: {str(e)}")

