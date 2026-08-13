from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import io
from inference import detect_log_type, predict_from_dataframes

app = FastAPI(title="Insider Threat Detection API")

# Allow Streamlit (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Insider Threat Detection API is running"}


@app.post("/analyze")
async def analyze_logs(files: list[UploadFile] = File(...)):
    raw_dataframes = []
    detected_types = []

    for file in files:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        log_type = detect_log_type(df)
        detected_types.append({"filename": file.filename, "detected_type": log_type})
        raw_dataframes.append((df, log_type))

    result = predict_from_dataframes(raw_dataframes)
    flagged = result[result["risk_category"].isin(["High", "Critical"])]

    return JSONResponse({
        "files_processed": detected_types,
        "total_user_days_scored": len(result),
        "flagged_count": len(flagged),
        "all_results": result[["user", "day", "risk_score", "risk_category"]].astype(str).to_dict(orient="records"),
    })