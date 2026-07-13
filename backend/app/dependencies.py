"""Authentication and authorisation dependencies.

This is where RBAC is actually ENFORCED.

The distinction matters and it is the single most common security mistake in
projects like this: hiding a button in the React UI is not an access control.
The endpoint is still there, and anyone with curl can call it. Authorisation
has to happen on the server, before the handler runs. That is what these
dependencies do.

  get_current_user            - you are who you say you are (authentication)
  require_roles(...)          - and you are allowed to do this (authorisation)
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import SecurityUser, UserRole
from backend.app.security import decode_access_token

# tokenUrl is what FastAPI's /docs "Authorize" button posts to. It does not
# create the endpoint - it just tells Swagger where the login route lives.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> SecurityUser:
    """Resolve the JWT in the Authorization header to a live user.

    Note we re-fetch the user from the database rather than trusting the token's
    payload alone. The token says "user 7, role administrator" - but that was
    true when the token was MINTED. If user 7 has since been deactivated or
    demoted, the token still cheerfully claims otherwise, because a JWT cannot
    be revoked. So for anything that matters, we check the current state.

    That costs one indexed primary-key lookup per request. Worth it.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user = db.get(SecurityUser, int(user_id))
    except (ValueError, TypeError):
        raise credentials_exception from None

    if user is None:
        raise credentials_exception

    # A deactivated account is rejected even holding a valid, unexpired token.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    return user


CurrentUser = Annotated[SecurityUser, Depends(get_current_user)]


def require_roles(*allowed_roles: UserRole) -> Callable[[SecurityUser], SecurityUser]:
    """Build a dependency that admits only the listed roles.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_roles(UserRole.ADMINISTRATOR))])

    401 vs 403 is a real distinction, not pedantry:
      401 Unauthorized  - "I do not know who you are"      (bad/absent token)
      403 Forbidden     - "I know exactly who you are, and you may not do this"

    get_current_user raises the 401s. This raises the 403s.
    """

    def role_checker(current_user: CurrentUser) -> SecurityUser:
        if current_user.role not in allowed_roles:
            allowed = ", ".join(r.value for r in allowed_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{current_user.role.value}' is not permitted to "
                    f"perform this action. Requires one of: {allowed}."
                ),
            )
        return current_user

    return role_checker


# --- Convenience role bundles ----------------------------------------------
# Named for what they MEAN, not just which roles they contain. When the role
# model changes, these are the one place to update.

# Anyone who operates the platform.
ANY_OPERATOR = (
    UserRole.SECURITY_ANALYST,
    UserRole.SOC_ENGINEER,
    UserRole.SECURITY_MANAGER,
    UserRole.ADMINISTRATOR,
)

# Can see ground truth / insider labels. Deliberately NOT analysts: an analyst
# who can read the answer key is not investigating.
CAN_VIEW_GROUND_TRUTH = (UserRole.SECURITY_MANAGER, UserRole.ADMINISTRATOR)

# Can load or reload the dataset. Destructive and slow; admin only.
CAN_INGEST_DATA = (UserRole.ADMINISTRATOR,)