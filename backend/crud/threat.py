"""
CRUD operations for Threat Center.
"""

from sqlalchemy.orm import Session

from backend.database.models import Threat
from backend.schemas.threat import ThreatCreate, ThreatUpdate


# ============================================================
# Get All Threats
# ============================================================

def get_threats(db: Session):
    return (
        db.query(Threat)
        .order_by(Threat.created_at.desc())
        .all()
    )


# ============================================================
# Get Threat by ID
# ============================================================

def get_threat(db: Session, threat_id: int):
    return (
        db.query(Threat)
        .filter(Threat.id == threat_id)
        .first()
    )


# ============================================================
# Create Threat
# ============================================================

def create_threat(
    db: Session,
    threat: ThreatCreate,
):
    db_threat = Threat(**threat.model_dump())

    db.add(db_threat)
    db.commit()
    db.refresh(db_threat)

    return db_threat


# ============================================================
# Update Threat
# ============================================================

def update_threat(
    db: Session,
    threat_id: int,
    threat: ThreatUpdate,
):
    db_threat = get_threat(db, threat_id)

    if not db_threat:
        return None

    update_data = threat.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_threat, key, value)

    db.commit()
    db.refresh(db_threat)

    return db_threat


# ============================================================
# Delete Threat
# ============================================================

def delete_threat(
    db: Session,
    threat_id: int,
):
    db_threat = get_threat(db, threat_id)

    if not db_threat:
        return None

    db.delete(db_threat)
    db.commit()

    return db_threat


# ============================================================
# Resolve Threat
# ============================================================

def resolve_threat(
    db: Session,
    threat_id: int,
):
    db_threat = get_threat(db, threat_id)

    if not db_threat:
        return None

    db_threat.status = "Resolved"

    db.commit()
    db.refresh(db_threat)

    return db_threat
