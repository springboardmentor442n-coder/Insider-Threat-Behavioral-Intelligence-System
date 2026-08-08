"""JWT issuance and role-based access control."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from app.models import ROLE_LEVELS, Analyst


def issue_token(analyst: Analyst) -> tuple[str, int]:
    cfg = current_app.config
    expires_in = cfg["JWT_EXPIRY_MINUTES"] * 60
    now = datetime.now(timezone.utc)
    payload = {
        "sub": analyst.username,
        "uid": analyst.id,
        "role": analyst.role,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    token = jwt.encode(payload, cfg["JWT_SECRET"], algorithm=cfg["JWT_ALGORITHM"])
    return token, expires_in


def decode_token(token: str) -> dict | None:
    cfg = current_app.config
    try:
        return jwt.decode(token, cfg["JWT_SECRET"], algorithms=[cfg["JWT_ALGORITHM"]])
    except jwt.PyJWTError:
        return None


def _extract_token() -> str | None:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:].strip()
    # SSE via EventSource cannot set headers, so allow a query-string token.
    return request.args.get("token")


def require_auth(min_role: str = "viewer"):
    """Decorator enforcing a valid JWT and a minimum role level."""
    required_level = ROLE_LEVELS.get(min_role, 1)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            token = _extract_token()
            if not token:
                return jsonify({"error": "authorization required"}), 401
            claims = decode_token(token)
            if not claims:
                return jsonify({"error": "invalid or expired token"}), 401
            if ROLE_LEVELS.get(claims.get("role"), 0) < required_level:
                return (
                    jsonify(
                        {
                            "error": "insufficient privileges",
                            "required_role": min_role,
                            "your_role": claims.get("role"),
                        }
                    ),
                    403,
                )
            g.current_user = claims
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def current_username() -> str:
    return getattr(g, "current_user", {}).get("sub", "unknown")
