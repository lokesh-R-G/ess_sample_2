from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token
from app.db.mongo import get_database
from bson import ObjectId


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    emp_id = payload.get("sub") or payload.get("empId")
    if not emp_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    db = get_database()
    user = await db.users.find_one({"empId": emp_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    # remove internal _id and convert ObjectId fields to strings for JSON serialization
    user.pop("_id", None)
    for k, v in list(user.items()):
        if isinstance(v, ObjectId):
            user[k] = str(v)
    # Fetch authoritative employee mapping
    employee = await db.employees.find_one({"$or": [{"employeeCode": emp_id}, {"empId": emp_id}]})
    if employee:
        user["employeeId"] = employee.get("employeeId")
        user["employeeCode"] = employee.get("employeeCode", emp_id)
    else:
        user.setdefault("employeeId", payload.get("employeeId"))
        user.setdefault("employeeCode", payload.get("employeeCode"))
        
    return user


def require_roles(*allowed_roles: str):
    async def _role_guard(user=Depends(get_current_user)):
        user_role = (user.get("role") or "").lower()
        allowed = [r.lower() for r in allowed_roles]
        if user_role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _role_guard
