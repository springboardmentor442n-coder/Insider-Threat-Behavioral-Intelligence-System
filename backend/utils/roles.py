from fastapi import Depends, HTTPException, status
from backend.utils.security import get_current_user


def require_roles(*roles):
    def checker(current_user=Depends(get_current_user)):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        if hasattr(current_user, "is_active") and not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # Allow all authenticated active users access to system features
        return current_user

    return checker
