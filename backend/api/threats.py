from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.session import get_db

from backend.schemas.threat import (
    ThreatCreate,
    ThreatUpdate,
    ThreatResponse,
)

from backend.services.threat_service import (
    get_all_threats,
    get_threat_by_id,
    create_new_threat,
    update_existing_threat,
    delete_existing_threat,
    resolve_existing_threat,
)


router = APIRouter()


# ============================================================
# GET ALL THREATS
# ============================================================

@router.get("/")
def get_threats(
    db: Session = Depends(get_db),
):
    """
    Return ML-derived risky employees for Threat Center.

    This endpoint intentionally uses the existing employee
    behavioral intelligence pipeline rather than the legacy
    SQL Threat table.
    """

    return get_all_threats(db)


# ============================================================
# GET THREAT BY ID
# ============================================================

@router.get("/{threat_id}")
def get_threat(
    threat_id: int,
    db: Session = Depends(get_db),
):
    threat = get_threat_by_id(
        db,
        threat_id,
    )

    if threat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Threat not found",
        )

    return threat


# ============================================================
# CREATE THREAT
# ============================================================

@router.post(
    "/",
    response_model=ThreatResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_threat(
    threat: ThreatCreate,
    db: Session = Depends(get_db),
):
    return create_new_threat(
        db,
        threat,
    )


# ============================================================
# UPDATE THREAT
# ============================================================

@router.put(
    "/{threat_id}",
    response_model=ThreatResponse,
)
def update_threat(
    threat_id: int,
    threat: ThreatUpdate,
    db: Session = Depends(get_db),
):
    updated = update_existing_threat(
        db,
        threat_id,
        threat,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Threat not found",
        )

    return updated


# ============================================================
# DELETE THREAT
# ============================================================

@router.delete("/{threat_id}")
def delete_threat(
    threat_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_existing_threat(
        db,
        threat_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Threat not found",
        )

    return {
        "message": "Threat deleted successfully"
    }


# ============================================================
# RESOLVE THREAT
# ============================================================

@router.post(
    "/{threat_id}/resolve",
    response_model=ThreatResponse,
)
def resolve_threat(
    threat_id: int,
    db: Session = Depends(get_db),
):
    resolved = resolve_existing_threat(
        db,
        threat_id,
    )

    if resolved is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Threat not found",
        )

    return resolved
