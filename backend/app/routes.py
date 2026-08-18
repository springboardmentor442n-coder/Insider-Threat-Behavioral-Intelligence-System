from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
import asyncio
import io
import pandas as pd
from pathlib import Path
from datetime import datetime

from .schemas import UserFeatures
from .predictor import predict, predict_batch
from ml.streaming.stream_data import stream_data

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PROJECT_ROOT / "datasets" / "processed" / "final_features.csv"

@router.get("/")
def home():
    return {
        "message": "Insider Threat Behavioral Intelligence System API is Running"
    }

@router.post("/predict")
def predict_user(user: UserFeatures):
    result = predict(user.model_dump())
    return {
        "prediction": result
    }

@router.post("/batch-predict")
async def batch_predict(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {str(e)}")
        
    required_cols = ['user', 'device_connections', 'emails_sent', 'files_accessed', 'websites_visited', 'logon_count', 'O', 'C', 'E', 'A', 'N']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing_cols)}")
        
    features = ['device_connections', 'emails_sent', 'files_accessed', 'websites_visited', 'logon_count', 'O', 'C', 'E', 'A', 'N']
    feature_df = df[features]
    
    predictions = predict_batch(feature_df)
    
    results = []
    normal_count = 0
    anomaly_count = 0
    
    for idx, row in df.iterrows():
        pred = predictions[idx]
        if pred == "NORMAL":
            normal_count += 1
            risk_level = "LOW"
        else:
            anomaly_count += 1
            risk_level = "HIGH"
            
        result_row = {
            "employeeId": str(row['user']),
            "features": {f: float(row[f]) for f in features},
            "prediction": pred,
            "riskLevel": risk_level
        }
        results.append(result_row)
        
    return {
        "summary": {
            "total": len(results),
            "normal": normal_count,
            "anomaly": anomaly_count
        },
        "results": results
    }

@router.get("/employees")
def get_employees():
    df = pd.read_csv(DEFAULT_DATA_PATH)
    users = df["user"].tolist()
    return {"employees": users}

@router.get("/employees/{employee_id}/analysis")
def get_employee_analysis(employee_id: str):
    df = pd.read_csv(DEFAULT_DATA_PATH)
    employee_row = df[df["user"] == employee_id]
    
    if employee_row.empty:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    row = employee_row.iloc[0]
    
    features = {
        "device_connections": float(row["device_connections"]),
        "emails_sent": float(row["emails_sent"]),
        "files_accessed": float(row["files_accessed"]),
        "websites_visited": float(row["websites_visited"]),
        "logon_count": float(row["logon_count"]),
        "O": float(row["O"]),
        "C": float(row["C"]),
        "E": float(row["E"]),
        "A": float(row["A"]),
        "N": float(row["N"])
    }
    
    prediction_result = predict(features)
    
    return {
        "employeeId": employee_id,
        "features": features,
        "prediction": prediction_result,
        "model": "Isolation Forest",
        "timestamp": datetime.now().isoformat()
    }


@router.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    stream_gen = stream_data(DEFAULT_DATA_PATH)
    try:
        while True:
            row = next(stream_gen)
            
            features = {
                "device_connections": float(row["device_connections"]),
                "emails_sent": float(row["emails_sent"]),
                "files_accessed": float(row["files_accessed"]),
                "websites_visited": float(row["websites_visited"]),
                "logon_count": float(row["logon_count"]),
                "O": float(row["O"]),
                "C": float(row["C"]),
                "E": float(row["E"]),
                "A": float(row["A"]),
                "N": float(row["N"])
            }
            
            prediction_result = predict(features)
            risk_level = "HIGH" if prediction_result == "ANOMALY" else "LOW"
            
            payload = {
                "employeeId": str(row["user"]),
                "activity": {
                    "deviceConnections": float(row["device_connections"]),
                    "emailsSent": float(row["emails_sent"]),
                    "filesAccessed": float(row["files_accessed"]),
                    "websitesVisited": float(row["websites_visited"]),
                    "logonCount": float(row["logon_count"])
                },
                "ocean": {
                    "O": float(row["O"]),
                    "C": float(row["C"]),
                    "E": float(row["E"]),
                    "A": float(row["A"]),
                    "N": float(row["N"])
                },
                "prediction": prediction_result,
                "riskLevel": risk_level
            }
            
            await websocket.send_json(payload)
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        print("Client disconnected from stream")
    except Exception as e:
        print(f"Error in stream: {e}")