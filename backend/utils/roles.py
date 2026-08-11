from fastapi import Depends, HTTPException, status
from backend.utils.security import get_current_user


def require_roles(*roles):
    def checker(current_user=Depends(get_current_user)):

        print("=" * 60)
        print("Current User :", current_user.username)
        print("Current Role :", current_user.role)
        print("Allowed Roles:", roles)
        print("=" * 60)

        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )

        return current_user

    return checker
