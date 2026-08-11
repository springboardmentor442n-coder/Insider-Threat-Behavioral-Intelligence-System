import io
import pandas as pd
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.risk_record import BehavioralRiskRecord
from app.models.alert import SecurityAlert
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.ml.predictor import predictor_service
from app.services.cert_aggregator import cert_aggregator

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
def run_single_prediction(req: PredictionRequest):
    """
    POST /api/analysis/predict (or /api/v1/analysis/predict)
    Predict threat level and risk scores for a single 19-feature input vector.
    """
    if not predictor_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model inference unavailable: Model or Scaler artifacts are not loaded into memory."
        )

    feature_dict = req.model_dump()
    return predictor_service.predict(feature_dict)

@router.post("/upload")
async def analyze_csv_upload(
    file: Optional[UploadFile] = File(None),
    logon_file: Optional[UploadFile] = File(None),
    device_file: Optional[UploadFile] = File(None),
    file_file: Optional[UploadFile] = File(None),
    email_file: Optional[UploadFile] = File(None),
    http_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    POST /api/analysis/upload
    Bulk Analysis Endpoint supporting Mode 1 (Feature CSV) and Mode 2 (Raw CERT CSVs).
    """
    if not predictor_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model inference unavailable: Trained model artifacts (gb.pkl, scaler.pkl) not loaded."
        )

    df = None
    upload_mode = None

    if file is not None:
        filename = file.filename.lower()
        if not filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Unsupported file type: Only CSV files are supported.")
        
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")
        
        try:
            df_input = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")

        missing_19 = [col for col in predictor_service.feature_columns if col not in df_input.columns]
        if not missing_19:
            df = df_input
            upload_mode = "Mode 1: Feature-Engineered CSV"
        else:
            if any(col in df_input.columns for col in ["activity", "filename", "url", "to", "attachment_count"]):
                if "activity" in df_input.columns:
                    sample_act = df_input["activity"].dropna().astype(str).str.lower().unique()
                    if any(a in sample_act for a in ["logon", "logoff"]):
                        df = cert_aggregator.process_raw_logs(logon_df=df_input)
                    else:
                        df = cert_aggregator.process_raw_logs(device_df=df_input)
                elif "filename" in df_input.columns:
                    df = cert_aggregator.process_raw_logs(file_df=df_input)
                elif "to" in df_input.columns or "attachment_count" in df_input.columns:
                    df = cert_aggregator.process_raw_logs(email_df=df_input)
                elif "url" in df_input.columns:
                    df = cert_aggregator.process_raw_logs(http_df=df_input)
                upload_mode = "Mode 2: Raw CERT Single File"
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing expected 19 feature columns: {missing_19}."
                )

    elif any(f is not None for f in [logon_file, device_file, file_file, email_file, http_file]):
        async def parse_raw(ufile: Optional[UploadFile]):
            if ufile is None:
                return None
            c = await ufile.read()
            if not c:
                return None
            return pd.read_csv(io.BytesIO(c))

        logon_df = await parse_raw(logon_file)
        device_df = await parse_raw(device_file)
        file_df = await parse_raw(file_file)
        email_df = await parse_raw(email_file)
        http_df = await parse_raw(http_file)

        df = cert_aggregator.process_raw_logs(
            logon_df=logon_df,
            device_df=device_df,
            file_df=file_df,
            email_df=email_df,
            http_df=http_df
        )
        upload_mode = "Mode 2: Raw CERT Multiple Log Files"
    else:
        raise HTTPException(
            status_code=400,
            detail="No data provided. Upload either a 19-feature CSV file or raw CERT activity log files (logon, device, file, email, http)."
        )

    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="Could not extract any valid daily user activity from the uploaded files.")

    total_rows = len(df)
    successful_rows = 0
    failed_rows = 0
    validation_errors = []
    detailed_results = []

    normal_count = 0
    suspicious_count = 0
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0

    for idx, row in df.iterrows():
        row_num = idx + 1
        user = str(row.get("user", f"USR_{(idx+1):04d}"))
        day = str(row.get("day", pd.Timestamp.now().strftime("%Y-%m-%d")))

        row_feature_dict = {}
        row_failed = False

        for col in predictor_service.feature_columns:
            val = row.get(col, 0)
            if pd.isna(val):
                validation_errors.append({"row": row_num, "column": col, "error": "Value is missing/null"})
                row_failed = True
                break
            try:
                num_val = float(val)
                if num_val < 0:
                    validation_errors.append({"row": row_num, "column": col, "error": f"Negative value ({val}) invalid"})
                    row_failed = True
                    break
                row_feature_dict[col] = num_val
            except (ValueError, TypeError):
                validation_errors.append({"row": row_num, "column": col, "error": f"Invalid numeric format ({val})"})
                row_failed = True
                break

        if row_failed:
            failed_rows += 1
            continue

        try:
            res = predictor_service.predict(row_feature_dict)

            rec = BehavioralRiskRecord(
                user=user,
                day=day,
                logon_count=int(row_feature_dict["logon_count"]),
                logoff_count=int(row_feature_dict["logoff_count"]),
                off_hours_logons=int(row_feature_dict["off_hours_logons"]),
                unique_pcs=int(row_feature_dict["unique_pcs"]),
                device_connects=int(row_feature_dict["device_connects"]),
                device_disconnects=int(row_feature_dict["device_disconnects"]),
                unique_device_pcs=int(row_feature_dict["unique_device_pcs"]),
                file_activity_count=int(row_feature_dict["file_activity_count"]),
                unique_file_pcs=int(row_feature_dict["unique_file_pcs"]),
                unique_files=int(row_feature_dict["unique_files"]),
                sensitive_file_count=int(row_feature_dict["sensitive_file_count"]),
                email_count=int(row_feature_dict["email_count"]),
                attachment_count=int(row_feature_dict["attachment_count"]),
                total_email_size=float(row_feature_dict["total_email_size"]),
                unique_email_pcs=int(row_feature_dict["unique_email_pcs"]),
                external_email_count=int(row_feature_dict["external_email_count"]),
                http_request_count=int(row_feature_dict["http_request_count"]),
                unique_http_urls=int(row_feature_dict["unique_http_urls"]),
                off_hours_http=int(row_feature_dict["off_hours_http"]),
                prediction=res["prediction"],
                prediction_probability=res["prediction_probability"],
                ml_risk_score=res["ml_risk_score"],
                behavioral_risk_score=res["behavioral_risk_score"],
                final_risk_score=res["final_risk_score"],
                severity=res["severity"]
            )
            db.add(rec)

            if res["final_risk_score"] >= 60 or res["severity"] in ["High", "Critical"]:
                alert = SecurityAlert(
                    user=user,
                    day=day,
                    severity=res["severity"],
                    final_risk_score=res["final_risk_score"],
                    status="New",
                    title=f"High Risk Behavior Detected ({res['severity']})",
                    description=f"User {user} registered final risk score of {res['final_risk_score']} on {day}."
                )
                db.add(alert)

            successful_rows += 1

            if res["prediction"] == 1:
                suspicious_count += 1
            else:
                normal_count += 1

            sev = res["severity"]
            if sev == "Critical":
                critical_count += 1
            elif sev == "High":
                high_count += 1
            elif sev == "Medium":
                medium_count += 1
            else:
                low_count += 1

            detailed_results.append({
                "user": user,
                "day": day,
                "prediction": res["prediction"],
                "prediction_probability": res["prediction_probability"],
                "ml_risk_score": res["ml_risk_score"],
                "behavioral_risk_score": res["behavioral_risk_score"],
                "final_risk_score": res["final_risk_score"],
                "severity": res["severity"]
            })

        except Exception as e:
            failed_rows += 1
            validation_errors.append({"row": row_num, "error": f"Prediction failure: {str(e)}"})

    db.commit()

    return {
        "analysis_id": 1,
        "mode": upload_mode,
        "total_rows": total_rows,
        "successful_rows": successful_rows,
        "failed_rows": failed_rows,
        "normal_predictions": normal_count,
        "suspicious_predictions": suspicious_count,
        "critical_results": critical_count,
        "high_results": high_count,
        "medium_results": medium_count,
        "low_results": low_count,
        "validation_errors": validation_errors,
        "detailed_results": detailed_results
    }

@router.get("/{analysis_id}")
def get_analysis_summary(analysis_id: int, db: Session = Depends(get_db)):
    total_records = db.query(BehavioralRiskRecord).count()
    normal_count = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.prediction == 0).count()
    suspicious_count = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.prediction == 1).count()

    return {
        "analysis_id": analysis_id,
        "total_records": total_records,
        "normal_predictions": normal_count,
        "suspicious_predictions": suspicious_count,
        "status": "Completed"
    }

@router.get("/{analysis_id}/results")
def get_analysis_results(
    analysis_id: int,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    records = db.query(BehavioralRiskRecord).order_by(BehavioralRiskRecord.id.desc()).offset(offset).limit(limit).all()
    return [
        {
            "id": r.id,
            "user": r.user,
            "day": r.day,
            "prediction": r.prediction,
            "prediction_probability": r.prediction_probability,
            "ml_risk_score": r.ml_risk_score,
            "behavioral_risk_score": r.behavioral_risk_score,
            "final_risk_score": r.final_risk_score,
            "severity": r.severity
        }
        for r in records
    ]

@router.get("/{analysis_id}/download")
@router.get("/export")
def export_analysis_results_csv(
    limit: int = Query(50000, ge=1),
    db: Session = Depends(get_db)
):
    """
    GET /api/analysis/{analysis_id}/download (or /export)
    Download generated prediction results as analysis_results.csv
    """
    records = db.query(BehavioralRiskRecord).order_by(BehavioralRiskRecord.id.desc()).limit(limit).all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No analysis records available to export.")

    data = []
    for r in records:
        data.append({
            "User": r.user,
            "Day": r.day,
            "Prediction": r.prediction,
            "Prediction Probability": r.prediction_probability,
            "ML Risk Score": r.ml_risk_score,
            "Behavioral Risk Score": r.behavioral_risk_score,
            "Final Risk Score": r.final_risk_score,
            "Severity": r.severity
        })

    export_df = pd.DataFrame(data)
    stream = io.StringIO()
    export_df.to_csv(stream, index=False)
    
    response = StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=analysis_results.csv"
    return response
