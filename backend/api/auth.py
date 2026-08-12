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


from backend.services.auth_service import (
    register_user,
    login_user,
    get_all_users,
    update_user_role_service,
    update_user_status_service,
)
from backend.utils.roles import require_roles

@router.get("/users")
def list_users(current_user=Depends(require_roles("Administrator", "admin"))):
    """
    List all registered users.
    """
    return get_all_users()


@router.patch("/users/{user_id}/role")
def update_role(
    user_id: int,
    role: str,
    current_user=Depends(require_roles("Administrator", "admin")),
):
    updated = update_user_role_service(user_id, role)
    if not updated:
        raise HTTPException(404, "User not found")
    return updated


@router.patch("/users/{user_id}/status")
def update_status(
    user_id: int,
    is_active: bool,
    current_user=Depends(require_roles("Administrator", "admin")),
):
    updated = update_user_status_service(user_id, is_active)
    if not updated:
        raise HTTPException(404, "User not found")
    return updated


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
        "role": getattr(user, "role", "Security Analyst") or "Security Analyst",
        "is_active": user.is_active,
        "created_at": user.created_at,
    }
