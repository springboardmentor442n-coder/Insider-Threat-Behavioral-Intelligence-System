"""Persistence layer: analysts, alert case state and the audit trail."""

from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timezone

from app.extensions import db


def utcnow() -> datetime:
    """Naive UTC timestamp.

    Stored naive so the `.isoformat() + "Z"` rendering in to_dict() stays
    correct; datetime.utcnow() itself is deprecated.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)

# Role hierarchy — a role grants everything at or below its level.
ROLE_LEVELS = {"viewer": 1, "analyst": 2, "admin": 3}

PBKDF2_ROUNDS = 260_000


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ROUNDS
    ).hex()
    return f"pbkdf2_sha256${PBKDF2_ROUNDS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, rounds, salt, digest = stored.split("$")
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt), int(rounds)
        ).hex()
        return hmac.compare_digest(candidate, digest)
    except (ValueError, AttributeError):
        return False


class Analyst(db.Model):
    __tablename__ = "analysts"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="analyst")
    full_name = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password: str):
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    @property
    def level(self) -> int:
        return ROLE_LEVELS.get(self.role, 0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "full_name": self.full_name,
            "last_login": self.last_login.isoformat() + "Z" if self.last_login else None,
        }


class AlertCase(db.Model):
    """Analyst-managed state for a (user, day) alert."""

    __tablename__ = "alert_cases"
    __table_args__ = (db.UniqueConstraint("subject_user", "day", name="uq_case_subject_day"),)

    id = db.Column(db.Integer, primary_key=True)
    subject_user = db.Column(db.String(64), nullable=False, index=True)
    day = db.Column(db.String(16), nullable=False)
    risk_score = db.Column(db.Float, nullable=False, default=0.0)
    severity = db.Column(db.String(16), nullable=False, default="LOW")
    status = db.Column(db.String(32), nullable=False, default="OPEN")
    assigned_to = db.Column(db.String(64))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    VALID_STATUSES = ("OPEN", "IN_REVIEW", "ESCALATED", "CONFIRMED", "DISMISSED")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user": self.subject_user,
            "day": self.day,
            "risk_score": round(self.risk_score, 2),
            "severity": self.severity,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "notes": self.notes,
            "updated_at": self.updated_at.isoformat() + "Z" if self.updated_at else None,
        }


class AuditLog(db.Model):
    """Append-only record of analyst actions."""

    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    actor = db.Column(db.String(64), index=True)
    action = db.Column(db.String(64), nullable=False)
    target = db.Column(db.String(128))
    detail = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "actor": self.actor,
            "action": self.action,
            "target": self.target,
            "detail": self.detail,
            "at": self.created_at.isoformat() + "Z" if self.created_at else None,
        }


def record_audit(actor: str, action: str, target: str = None, detail: str = None):
    db.session.add(AuditLog(actor=actor, action=action, target=target, detail=detail))
    db.session.commit()


def seed_analysts(seed_config: dict):
    """Create the default analyst accounts on first boot."""
    created = []
    for username, (password, role) in seed_config.items():
        if db.session.query(Analyst).filter_by(username=username).first():
            continue
        analyst = Analyst(username=username, role=role, full_name=username.title())
        analyst.set_password(password)
        db.session.add(analyst)
        created.append(username)
    if created:
        db.session.commit()
    return created
