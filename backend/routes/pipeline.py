from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pathlib import Path

from backend.config import get_db
from ml.pipeline import run_pipeline

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_FOLDER = BASE_DIR / "dataset" / "raw"


@router.post("/run-pipeline")
async def execute_pipeline(
    db: Session = Depends(get_db)
):
    result = run_pipeline(
        dataset_folder=DATASET_FOLDER,
        db=db
    )

    return result