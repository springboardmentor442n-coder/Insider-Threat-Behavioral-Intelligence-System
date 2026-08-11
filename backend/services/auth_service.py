"""
Authentication Service

Handles user registration, login, and retrieval using PostgreSQL.
"""

from sqlalchemy.orm import Session

from backend.database.session import SessionLocal
from backend.repositories.user_repository import (
    create_user,
    get_all_users as repo_get_all_users,
    get_user_by_username as repo_get_user_by_username,
)
from backend.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
)


def register_user(
    username: str,
    password: str,
    role: str,
):
    """
    Register a new user.
    """

    db: Session = SessionLocal()

    try:

        existing_user = repo_get_user_by_username(
            db,
            username,
        )

        if existing_user:
            return None

        user = create_user(
            db=db,
            username=username,
            password_hash=hash_password(password),
            role=role,
        )

        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
        }

    finally:
        db.close()


def login_user(
    username: str,
    password: str,
):
    """
    Authenticate user and generate JWT.
    """

    db: Session = SessionLocal()

    try:

        user = repo_get_user_by_username(
            db,
            username,
        )

        if user is None:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        access_token = create_access_token(
            {
                "sub": user.username,
                "role": user.role,
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    finally:
        db.close()


def get_user_by_username(
    username: str,
):
    """
    Return a user object by username.
    """

    db: Session = SessionLocal()

    try:

        return repo_get_user_by_username(
            db,
            username,
        )

    finally:
        db.close()


def get_all_users():
    """
    Return all registered users.
    """

    db: Session = SessionLocal()

    try:

        users = repo_get_all_users(db)

        return [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active,
            }
            for user in users
        ]

    finally:
        db.close()
        