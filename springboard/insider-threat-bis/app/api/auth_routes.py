"""Authentication endpoints."""

from flask import Blueprint, g, jsonify, request

from app.auth import current_username, issue_token, require_auth
from app.extensions import db
from app.models import Analyst, AuditLog, record_audit, utcnow

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    analyst = db.session.query(Analyst).filter_by(username=username).first()
    if not analyst or not analyst.check_password(password):
        # Deliberately identical response for unknown user and wrong password.
        return jsonify({"error": "invalid credentials"}), 401

    analyst.last_login = utcnow()
    db.session.commit()
    record_audit(username, "LOGIN", detail=f"role={analyst.role}")

    token, expires_in = issue_token(analyst)
    return jsonify(
        {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "analyst": analyst.to_dict(),
        }
    )


@bp.get("/me")
@require_auth("viewer")
def me():
    analyst = db.session.query(Analyst).filter_by(username=g.current_user["sub"]).first()
    if not analyst:
        return jsonify({"error": "account no longer exists"}), 401
    return jsonify(analyst.to_dict())


@bp.post("/logout")
@require_auth("viewer")
def logout():
    record_audit(current_username(), "LOGOUT")
    return jsonify({"status": "logged out"})


@bp.get("/audit")
@require_auth("admin")
def audit():
    limit = min(int(request.args.get("limit", 100)), 500)
    rows = (
        db.session.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return jsonify({"count": len(rows), "entries": [r.to_dict() for r in rows]})
