"""Authentication endpoints: register, login, whoami."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.database import get_db
from backend.app.dependencies import CurrentUser
from backend.app.models import AuditLog, SecurityUser
from backend.app.ratelimit import limiter
from backend.app.schemas import (
    LogoutRequest,
    PasswordChangeRequest,
    RefreshRequest,
    Token,
    UserRegister,
    UserResponse,
)
from backend.app.security import (
    LOCKOUT_MINUTES,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_locked_out,
    password_problems,
    register_failed_login,
    register_successful_login,
    revoke_token,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])
settings = get_settings()


def _audit(
    db: Session,
    action: str,
    user_id: int | None,
    detail: str | None,
    request: Request,
) -> None:
    """Record an operator action.

    Deliberately does NOT commit - the caller owns the transaction, so the audit
    entry and the thing it describes either both land or neither does. An audit
    log that records events which were then rolled back is worse than no audit
    log, because it is confidently wrong.
    """
    db.add(
        AuditLog(
            security_user_id=user_id,
            action=action,
            detail=detail,
            ip_address=request.client.host if request.client else None,
        )
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new platform operator",
)
# Five an hour. Nobody legitimately creates six operator accounts in an hour.
# An attacker who has compromised one account and is quietly seeding themselves a
# few backdoors before anyone notices, does.
#
# NOTE THE DECORATOR ORDER. @limiter.limit must sit BELOW @router.post - it has to
# wrap the function before FastAPI registers it as a route. Put it above and it
# decorates the APIRoute object instead of the endpoint, and the limit silently
# never fires. The code looks correct, the tests pass, and the control does nothing.
@limiter.limit("5/hour")
def register(
    payload: UserRegister,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> SecurityUser:
    """Create a new operator account (analyst, SOC engineer, manager, or admin).

    Open registration is acceptable for this project's scope. A real deployment
    would put this behind an administrator invite - you do not let strangers
    self-provision accounts on a security monitoring platform. Noted as a
    hardening item rather than pretended away.
    """
    existing = db.scalar(
        select(SecurityUser).where(SecurityUser.email == payload.email)
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # ENFORCE THE PASSWORD POLICY.
    #
    # Before this, register() accepted "a" as a password. On a product that
    # surveils a thousand employees and stores the ground-truth list of who the
    # insiders are, that is not a small omission.
    #
    # The check returns EVERY reason at once, and says what they are. A policy that
    # only says "password too weak" trains people to append "1!" until it stops
    # complaining - which produces precisely the passwords the policy exists to
    # prevent.
    problems = password_problems(payload.password)
    if problems:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Password does not meet policy.", "problems": problems},
        )

    user = SecurityUser(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.flush()  # assigns user.id without committing yet

    _audit(
        db,
        action="user.register",
        user_id=user.id,
        detail=f"role={payload.role.value}",
        request=request,
    )

    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token, summary="Exchange credentials for a JWT")
# TEN A MINUTE.
#
# The account lockout stops an attacker guessing one account's password. It does
# nothing about PASSWORD SPRAYING: one password ("Autumn2025!") tried against a
# thousand accounts. Every account sees a single failed login, so no lockout ever
# fires - and in an organisation of any size, somebody is using that password.
#
# Lockout is per-ACCOUNT. This is per-IP. They defend against different attacks and
# neither substitutes for the other.
@limiter.limit("10/minute")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Authenticate and return an access token.

    Uses OAuth2PasswordRequestForm (form-encoded `username`/`password`) rather
    than a JSON body. That is what makes the "Authorize" button work in FastAPI's
    /docs, and it is the standard clients expect. Our `username` field carries
    the email.

    Note the error message is identical for "no such user" and "wrong password".
    Distinguishing them would hand an attacker a free user-enumeration oracle:
    they could discover which emails have accounts simply by watching which ones
    produce a different error.
    """
    user = db.scalar(
        select(SecurityUser).where(SecurityUser.email == form_data.username)
    )

    # --- LOCKOUT CHECK, BEFORE THE PASSWORD IS EVEN LOOKED AT ---------------
    #
    # Order matters. Check the lock FIRST, or a locked-out attacker can keep
    # guessing and simply ignore the 401s - the lockout would be decorative.
    if user is not None and is_locked_out(user):
        _audit(
            db,
            action="auth.login_blocked_locked",
            user_id=user.id,
            detail=f"locked until {user.locked_until.isoformat()}",
            request=request,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Too many failed attempts. This account is locked for "
                f"{LOCKOUT_MINUTES} minutes."
            ),
        )

    if user is None or not verify_password(form_data.password, user.hashed_password):
        # Count the failure and lock after MAX_FAILED_LOGINS.
        #
        # Without this, /login is an unlimited password-guessing oracle: an attacker
        # with a wordlist and a weekend gets in, and nothing in the logs looks
        # unusual, because every individual request is a perfectly ordinary failed
        # login. Five strikes, then fifteen minutes in the corner.
        if user is not None:
            register_failed_login(user)

        _audit(
            db,
            action="auth.login_failed",
            user_id=user.id if user else None,
            detail=(
                f"email={form_data.username} "
                f"attempt={user.failed_login_attempts if user else '?'}"
            ),
            request=request,
        )
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    # Success wipes the slate: the failure counter resets and any lock lifts.
    register_successful_login(user)
    _audit(db, action="auth.login", user_id=user.id, detail=None, request=request)
    db.commit()

    access = create_access_token(subject=str(user.id), role=user.role.value)
    refresh, _jti = create_refresh_token(subject=str(user.id))

    return Token(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse, summary="The current operator")
def read_current_user(current_user: CurrentUser) -> SecurityUser:
    """Return the authenticated operator.

    Also the cheapest way for a client to check whether its stored token is
    still valid: a 200 means yes, a 401 means log in again.
    """
    return current_user


@router.post(
    "/refresh",
    response_model=Token,
    summary="Exchange a refresh token for a new access token",
)
def refresh(
    payload: RefreshRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Mint a fresh access token from a refresh token.

    WHY THIS EXISTS
    ---------------
    The access token now lives fifteen minutes. That is deliberate: it is sent on
    every request, so it is the token most likely to leak - into a log, a proxy, an
    error report, a browser extension - and fifteen minutes is the blast radius of
    that leak.

    But an analyst working an incident cannot re-enter their password every quarter
    of an hour. In practice, people respond to that by picking weaker passwords,
    which makes the system LESS secure. So the refresh token carries the session,
    and this endpoint quietly renews the access token behind the scenes.

    THE CHECK THAT MATTERS
    ----------------------
    The token's `type` claim must be "refresh". Skip that and an attacker who steals
    a refresh token can present it as an access token - the two are structurally
    identical JWTs signed with the same key - and turn a fifteen-minute window into
    seven days.

    The user's `is_active` flag is re-read from the DATABASE here, not trusted from
    the token. A deactivated account must stop working immediately, not whenever its
    current token happens to expire.
    """
    claims = decode_token(payload.refresh_token, expected_type="refresh")
    if claims is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(SecurityUser, int(claims["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    _audit(db, action="auth.refresh", user_id=user.id, detail=None, request=request)
    db.commit()

    access = create_access_token(subject=str(user.id), role=user.role.value)
    return Token(
        access_token=access,
        refresh_token=payload.refresh_token,   # the refresh token is not rotated
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Revoke a token")
def logout(
    payload: LogoutRequest,
    request: Request,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Revoke the caller's tokens. This is what makes "log out" mean something.

    BEFORE THIS ENDPOINT EXISTED, LOGGING OUT WAS A LIE.

    A JWT is self-validating: the server checks the signature and the expiry and
    asks nobody's permission. So "log out" meant "delete the token from your own
    browser" - and a token that had already been copied stayed perfectly valid for
    its full lifetime. There was no mechanism to stop it. On a product that surveils
    a thousand employees, that is not an acceptable answer.

    Revoking by `jti` - the token's unique ID - closes it.

    THE HONEST LIMITATION: the revocation list is an in-memory Python set. It does
    not survive a restart, and two uvicorn workers have two different sets. The
    correct production answer is Redis with a TTL equal to the token's own expiry,
    so entries evict themselves exactly when they stop mattering. That is a real
    dependency and adding a datastore for one feature is a real decision - so it is
    made deliberately and written down, rather than made accidentally and discovered
    during an incident.
    """
    revoked = 0
    if payload.refresh_token and revoke_token(payload.refresh_token):
        revoked += 1

    # Also revoke the ACCESS token the caller is holding right now - otherwise
    # "logout" leaves them with up to fifteen more minutes of access, which is
    # exactly the thing we are trying to stop.
    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        if revoke_token(auth_header.split(" ", 1)[1]):
            revoked += 1

    _audit(
        db,
        action="auth.logout",
        user_id=current_user.id,
        detail=f"revoked {revoked} token(s)",
        request=request,
    )
    db.commit()


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change your own password",
)
def change_password(
    payload: PasswordChangeRequest,
    request: Request,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Change the caller's password.

    THE CURRENT PASSWORD IS REQUIRED, AND THAT IS NOT A FORMALITY.

    Without it, anyone holding a stolen access token could change the victim's
    password and lock them out of their own account permanently - converting a
    fifteen-minute token theft into a total account takeover. Re-authenticating
    here means the attacker needs the password they were trying to steal.
    """
    if not verify_password(payload.current_password, current_user.hashed_password):
        _audit(
            db,
            action="auth.password_change_failed",
            user_id=current_user.id,
            detail="wrong current password",
            request=request,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect.",
        )

    problems = password_problems(payload.new_password)
    if problems:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Password does not meet policy.", "problems": problems},
        )

    current_user.hashed_password = hash_password(payload.new_password)
    current_user.password_changed_at = datetime.now(UTC)

    _audit(
        db,
        action="auth.password_changed",
        user_id=current_user.id,
        detail=None,
        request=request,
    )
    db.commit()