from fastapi import APIRouter, HTTPException

from backend.schemas import LoginRequest, TokenResponse
from backend.security import verify_password, create_access_token

router = APIRouter()

ADMIN_USERNAME = "admin"

ADMIN_PASSWORD_HASH = "$2b$12$1883He2iv9xBomsK2HnbS.1TZw26q9m76q7WqYVKvQ/ufzT05bXTq"


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):

    if data.username != ADMIN_USERNAME:
        raise HTTPException(status_code=401, detail="Invalid username")

    if not verify_password(data.password, ADMIN_PASSWORD_HASH):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token(
        {"sub": data.username}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }