"""Operator account management. Spec Module 2: User Profile Management.

WHY THIS MODULE EXISTS
----------------------
The system had register, login, and /me - and nothing else. There was no way to
update a profile, no way for an administrator to change a role or deactivate an
account, and no way to list who actually has access to the platform.

On a product that surveils a thousand employees, "we cannot tell you who has
accounts, and we cannot revoke one" is not a gap in a feature list. It is a gap in
the security model.

THE PRIVILEGE RULES ARE THE INTERESTING PART
--------------------------------------------
Two of these endpoints could hand an attacker the entire platform if they were
written naively, and the guards below are not decoration:

  * A user must not be able to change their OWN role. Otherwise the lowest-
    privileged account on the system - a Security Analyst - promotes itself to
    Administrator in one request, and every RBAC check elsewhere becomes theatre.

  * An administrator must not be able to deactivate or demote the LAST remaining
    administrator. Otherwise a single misclick locks every human out of the
    platform permanently, and the only recovery is a manual UPDATE against the
    production database.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import CurrentUser, require_roles
from backend.app.models import AuditLog, SecurityUser, UserRole
from backend.app.schemas import (
    UserAdminUpdate,
    UserResponse,
    UserSelfUpdate,
)

router = APIRouter(prefix="/api/users", tags=["users"])

ADMIN_ONLY = (UserRole.ADMINISTRATOR,)


def _audit(db: Session, *, action: str, user_id: int | None,
           detail: str | None, request: Request) -> None:
    db.add(
        AuditLog(
            security_user_id=user_id,
            action=action,
            detail=detail,
            ip_address=request.client.host if request.client else None,
        )
    )


def _count_active_admins(db: Session, *, excluding: int | None = None) -> int:
    stmt = select(func.count()).select_from(SecurityUser).where(
        SecurityUser.role == UserRole.ADMINISTRATOR,
        SecurityUser.is_active.is_(True),
    )
    if excluding is not None:
        stmt = stmt.where(SecurityUser.id != excluding)
    return int(db.scalar(stmt) or 0)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update your own profile",
)
def update_own_profile(
    payload: UserSelfUpdate,
    request: Request,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> SecurityUser:
    """Update the caller's own name or email.

    NOTE WHAT IS NOT HERE: role.

    UserSelfUpdate deliberately has no `role` field, so there is no way to send one.
    If it did, the lowest-privileged account on the platform could promote itself to
    Administrator in a single request, and every RBAC check in the codebase would
    become decorative. Privilege escalation through a profile-update endpoint is one
    of the most common real-world API vulnerabilities there is, and the defence is
    not to validate the field - it is to not have the field.

    Password changes go through /api/auth/change-password, which requires the
    CURRENT password. Allowing a password change here, authenticated only by a
    bearer token, would turn a stolen fifteen-minute token into a permanent account
    takeover.
    """
    if payload.email is not None and payload.email != current_user.email:
        clash = db.scalar(
            select(SecurityUser).where(SecurityUser.email == payload.email)
        )
        if clash is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )
        current_user.email = payload.email

    if payload.full_name is not None:
        current_user.full_name = payload.full_name

    _audit(db, action="user.self_update", user_id=current_user.id,
           detail=None, request=request)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get(
    "",
    response_model=list[UserResponse],
    dependencies=[Depends(require_roles(*ADMIN_ONLY))],
    summary="List platform operators (administrator only)",
)
def list_operators(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    include_inactive: bool = False,
) -> list[SecurityUser]:
    """Who has access to this platform?

    Administrator only - the operator roster is itself sensitive. It tells you
    exactly which accounts to attack, and which of them are Security Managers (the
    ones who can read the ground-truth insider labels).
    """
    stmt = select(SecurityUser).order_by(SecurityUser.id)
    if not include_inactive:
        stmt = stmt.where(SecurityUser.is_active.is_(True))
    return list(db.scalars(stmt.limit(limit).offset(offset)).all())


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_roles(*ADMIN_ONLY))],
    summary="Change an operator's role or activation (administrator only)",
)
def admin_update_operator(
    user_id: int,
    payload: UserAdminUpdate,
    request: Request,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> SecurityUser:
    """Change another operator's role, or deactivate them.

    THREE GUARDS, AND EACH ONE IS LOAD-BEARING.

    1. YOU CANNOT CHANGE YOUR OWN ROLE.
       Even as an administrator. This is not about trusting administrators - it is
       about limiting what a STOLEN administrator token can do quietly, and about
       making privilege changes visible to a second person. Self-promotion is the
       single most valuable action an attacker can take, so it does not exist as an
       operation.

    2. YOU CANNOT DEACTIVATE YOURSELF.
       An administrator who deactivates their own account has locked themselves out
       mid-request, and their next call fails with a 403 they cannot fix.

    3. YOU CANNOT REMOVE THE LAST ADMINISTRATOR.
       Demote or deactivate the only remaining admin and NOBODY can administer the
       platform, ever again. The only recovery is a manual UPDATE against the
       production database - which means an outage, a DBA, and an incident report.
       One misclick should not be able to do that.
    """
    target = db.get(SecurityUser, user_id)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such operator.",
        )

    # GUARD 1 + 2: no self-modification of role or activation.
    if target.id == current_user.id:
        if payload.role is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You cannot change your own role. Ask another administrator. "
                    "Self-promotion is the most valuable single action an attacker "
                    "with a stolen token can take, so it is not an operation this "
                    "system offers."
                ),
            )
        if payload.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot deactivate your own account.",
            )

    # GUARD 3: never strand the platform without an administrator.
    removing_admin = target.role == UserRole.ADMINISTRATOR and (
        (payload.role is not None and payload.role != UserRole.ADMINISTRATOR)
        or payload.is_active is False
    )
    if removing_admin and _count_active_admins(db, excluding=target.id) == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This is the last active administrator. Removing them would leave "
                "nobody able to administer the platform, and the only recovery "
                "would be a manual UPDATE against the production database. "
                "Promote another administrator first."
            ),
        )

    changes: list[str] = []
    if payload.role is not None and payload.role != target.role:
        changes.append(f"role {target.role.value} -> {payload.role.value}")
        target.role = payload.role
    if payload.is_active is not None and payload.is_active != target.is_active:
        changes.append(f"active {target.is_active} -> {payload.is_active}")
        target.is_active = payload.is_active
    if payload.full_name is not None:
        target.full_name = payload.full_name

    # Unlocking a brute-forced account is an administrative action, and one worth
    # having: five typos should not require a fifteen-minute wait if an admin is
    # sitting right there.
    if payload.unlock:
        target.failed_login_attempts = 0
        target.locked_until = None
        changes.append("unlocked")

    _audit(
        db,
        action="user.admin_update",
        user_id=current_user.id,
        detail=f"target={target.email}; " + ("; ".join(changes) or "no change"),
        request=request,
    )
    db.commit()
    db.refresh(target)
    return target