"""Security helpers for password hashing and JWT-based authentication."""

from datetime import datetime, timedelta

from jose import jwt, JWTError
from pwdlib import PasswordHash
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer

from backend.settings import settings


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=settings.oauth2_token_url
)


def hash_password(password: str):
    return password_hash.hash(password)


def verify_password(
    plain_password,
    hashed_password,
):
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(data: dict):
    """Create a signed access token for the supplied payload."""

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    to_encode.update(
        {"exp": expire}
    )

    token = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )

    print("\n========== TOKEN CREATED ==========")
    print("Payload :", to_encode)
    print("Token   :", token)
    print("===================================\n")

    return token


def verify_access_token(token: str):
    """Validate an access token and return the subject username."""

    print("\n========== VERIFY TOKEN ==========")
    print("Received Token:")
    print(token)

    try:

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        print("\nDecoded Payload:")
        print(payload)

        username = payload.get("sub")

        print("\nUsername from Token:")
        print(username)

        print("==================================\n")

        return username

    except JWTError as e:

        print("\nJWT ERROR:")
        print(e)
        print("==================================\n")

        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    """Resolve the currently authenticated user from a bearer token."""

    print("\n========== GET CURRENT USER ==========")
    print("Token received by OAuth2:")
    print(token)

    # Local import avoids circular imports
    from backend.services.auth_service import (
        get_user_by_username,
    )

    username = verify_access_token(token)

    if username is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = get_user_by_username(username)

    print("\nUser found:")
    print(user)

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    print("======================================\n")

    return user
