from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.risk_record import BehavioralRiskRecord
from app.ml.predictor import predictor_service
from typing import List, Optional

router = APIRouter()

@router.get("/explain/{record_id}")
def explain_record_risk(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail=f"Behavioral risk record ID {record_id} not found.")

    feature_dict = {
        "logon_count": rec.logon_count,
        "logoff_count": rec.logoff_count,
        "off_hours_logons": rec.off_hours_logons,
        "unique_pcs": rec.unique_pcs,
        "device_connects": rec.device_connects,
        "device_disconnects": rec.device_disconnects,
        "unique_device_pcs": rec.unique_device_pcs,
        "file_activity_count": rec.file_activity_count,
        "unique_file_pcs": rec.unique_file_pcs,
        "unique_files": rec.unique_files,
        "sensitive_file_count": rec.sensitive_file_count,
        "email_count": rec.email_count,
        "attachment_count": rec.attachment_count,
        "total_email_size": rec.total_email_size,
        "unique_email_pcs": rec.unique_email_pcs,
        "external_email_count": rec.external_email_count,
        "http_request_count": rec.http_request_count,
        "unique_http_urls": rec.unique_http_urls,
        "off_hours_http": rec.off_hours_http
    }

    importances = {}
    if predictor_service.is_loaded and predictor_service.model is not None:
        try:
            for feat, imp in zip(predictor_service.feature_columns, predictor_service.model.feature_importances_):
                importances[feat] = float(imp)
        except Exception:
            pass

    rule_evaluations = [
        {
            "rule": "Off-hours Logon Spike (> 2)",
            "feature": "off_hours_logons",
            "value": rec.off_hours_logons,
            "threshold": 2,
            "triggered": rec.off_hours_logons > 2,
            "impact": "High" if rec.off_hours_logons > 2 else "Normal"
        },
        {
            "rule": "Removable Media / USB Connects (> 5)",
            "feature": "device_connects",
            "value": rec.device_connects,
            "threshold": 5,
            "triggered": rec.device_connects > 5,
            "impact": "Critical" if rec.device_connects > 5 else "Normal"
        },
        {
            "rule": "Sensitive File Access (> 5)",
            "feature": "sensitive_file_count",
            "value": rec.sensitive_file_count,
            "threshold": 5,
            "triggered": rec.sensitive_file_count > 5,
            "impact": "High" if rec.sensitive_file_count > 5 else "Normal"
        },
        {
            "rule": "Email Attachment Exfiltration (> 10)",
            "feature": "attachment_count",
            "value": rec.attachment_count,
            "threshold": 10,
            "triggered": rec.attachment_count > 10,
            "impact": "High" if rec.attachment_count > 10 else "Normal"
        },
        {
            "rule": "External Email Recipient Spike (> 10)",
            "feature": "external_email_count",
            "value": rec.external_email_count,
            "threshold": 10,
            "triggered": rec.external_email_count > 10,
            "impact": "High" if rec.external_email_count > 10 else "Normal"
        },
        {
            "rule": "Off-hours Web Traffic Spike (> 10)",
            "feature": "off_hours_http",
            "value": rec.off_hours_http,
            "threshold": 10,
            "triggered": rec.off_hours_http > 10,
            "impact": "Medium" if rec.off_hours_http > 10 else "Normal"
        }
    ]

    # Feature risk contributions
    feature_contributions = []
    for feat in predictor_service.feature_columns:
        val = feature_dict.get(feat, 0)
        imp = importances.get(feat, 0.05)
        
        # Calculate transparent risk weight
        score_weight = round(val * imp * 10, 2)
        feature_contributions.append({
            "feature": feat,
            "value": val,
            "model_importance": round(imp, 4),
            "risk_contribution_score": score_weight,
            "status": "Suspicious Indicator" if score_weight > 5.0 else "Normal"
        })

    feature_contributions.sort(key=lambda x: x["risk_contribution_score"], reverse=True)

    return {
        "record_id": rec.id,
        "user": rec.user,
        "day": rec.day,
        "prediction": rec.prediction,
        "prediction_probability": rec.prediction_probability,
        "ml_risk_score": rec.ml_risk_score,
        "behavioral_risk_score": rec.behavioral_risk_score,
        "final_risk_score": rec.final_risk_score,
        "severity": rec.severity,
        "rule_evaluations": rule_evaluations,
        "top_contributing_features": feature_contributions[:10]
    }
