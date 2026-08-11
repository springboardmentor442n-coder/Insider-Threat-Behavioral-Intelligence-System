"""
User Repository

Provides all database operations related to users.
"""

from typing import Optional

from sqlalchemy.orm import Session

from backend.database.models import User


def get_user_by_username(
    db: Session,
    username: str,
) -> Optional[User]:
    """
    Fetch a user by username.
    """

    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def get_user_by_id(
    db: Session,
    user_id: int,
) -> Optional[User]:
    """
    Fetch a user by ID.
    """

    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def create_user(
    db: Session,
    username: str,
    password_hash: str,
    role: str,
):
    """
    Create a new user.
    """

    user = User(
        username=username,
        password_hash=password_hash,
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_all_users(db: Session):
    """
    Return all registered users.
    """

    return (
        db.query(User)
        .order_by(User.username)
        .all()
    )


def delete_user(
    db: Session,
    username: str,
):
    """
    Delete user by username.
    """

    user = get_user_by_username(
        db,
        username,
    )

    if user is None:
        return False

    db.delete(user)
    db.commit()

    return True
