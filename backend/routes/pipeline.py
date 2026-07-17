from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from pathlib import Path
import shutil

from backend.config import get_db
from ml.pipeline import run_pipeline

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]

UPLOAD_FOLDER = BASE_DIR / "backend" / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)


@router.post("/run-pipeline")
async def execute_pipeline(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    uploaded_file = UPLOAD_FOLDER / file.filename

    with open(uploaded_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = run_pipeline(
        input_csv=uploaded_file,
        db=db
    )

    return result