from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .core.security import decode_access_token
from .db.mongo import get_database


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    payload = decode_access_token(credentials.credentials)
    emp_id = payload.get("empId")
    if not emp_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    db = get_database()
    user = await db.users.find_one({"empId": emp_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_roles(*allowed_roles: str):
    async def _role_guard(user=Depends(get_current_user)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _role_guard
