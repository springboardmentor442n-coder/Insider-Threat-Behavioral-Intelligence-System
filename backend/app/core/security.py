import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import jwt
from app.core.config import settings

# Salt for password hashing
SALT = b"insider_threat_static_salt_2026_v1"

def get_password_hash(password: str) -> str:
    # Use PBKDF2 HMAC SHA256 for universal Python 3.13 compatibility
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), SALT, 100000)
    return key.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), SALT, 100000)
    return hmac.compare_digest(key.hex(), hashed_password)

def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
