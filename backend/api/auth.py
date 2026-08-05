"""
Authentication API Routes
"""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm

from backend.schemas.auth import (
    UserRegister,
)

from backend.services.auth_service import (
    register_user,
    login_user,
    get_all_users,
)

from backend.utils.security import (
    get_current_user,
)

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserRegister,
):
    """
    Register a new user.
    """

    new_user = register_user(
        username=user.username,
        password=user.password,
        role=user.role,
    )

    if new_user is None:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists.",
        )

    return {
        "message": "User registered successfully.",
        "user": new_user,
    }


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Login and receive JWT token.
    """

    token = login_user(
        username=form_data.username,
        password=form_data.password,
    )

    if token is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    return token


@router.get("/users")
def list_users():
    """
    List all registered users.
    """

    return get_all_users()


@router.get("/me")
def current_user(
    user=Depends(get_current_user),
):
    """
    Return authenticated user details.
    """

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }
