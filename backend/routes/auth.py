from fastapi import APIRouter, HTTPException

from backend.schemas import LoginRequest, TokenResponse
from backend.security import create_access_token

router = APIRouter()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "admin123"


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):

    print("Username received:", repr(data.username))
    print("Password received:", repr(data.password))

    if data.username != ADMIN_USERNAME:
        raise HTTPException(status_code=401, detail="Invalid username")

    if data.password != ADMIN_PASSWORD_HASH:
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({"sub": data.username})

    return {
        "access_token": token,
        "token_type": "bearer",
    }