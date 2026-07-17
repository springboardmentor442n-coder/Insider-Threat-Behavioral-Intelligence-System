from fastapi import APIRouter, UploadFile, File
import shutil
from pathlib import Path

router = APIRouter()

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    file_path = UPLOAD_FOLDER / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "CSV uploaded successfully",
        "filename": file.filename
    }