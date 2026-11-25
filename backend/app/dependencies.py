from __future__ import annotations

from fastapi import Depends, HTTPException, status, Header, Request
from app.rbac.engine import authorize, has_permission
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
    if not user.get("isActive", True) or user.get("status") == "inactive":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive. Access denied.")
    # remove internal _id and convert ObjectId fields to strings for JSON serialization
    user.pop("_id", None)
    for k, v in list(user.items()):
        if isinstance(v, ObjectId):
            user[k] = str(v)
    # Fetch authoritative employee mapping
    candidate_ids = set()
    if emp_id:
        candidate_ids.add(str(emp_id))
    if user.get("employeeCode"):
        candidate_ids.add(str(user["employeeCode"]))
    if user.get("employeeId"):
        candidate_ids.add(str(user["employeeId"]))
    if payload.get("employeeCode"):
        candidate_ids.add(str(payload["employeeCode"]))
    if payload.get("employeeId"):
        candidate_ids.add(str(payload["employeeId"]))

    # Pass 1: Resolve directly linked employee documents
    emp_clauses = []
    for cid in candidate_ids:
        emp_clauses.extend([{"employeeCode": cid}, {"empId": cid}, {"employeeId": cid}])

    matched_emps = await db.employees.find({"$or": emp_clauses}).to_list(10) if emp_clauses else []
    for me in matched_emps:
        if me.get("employeeId"):
            candidate_ids.add(str(me["employeeId"]))
        if me.get("employeeCode"):
            candidate_ids.add(str(me["employeeCode"]))

    # Pass 2: Secondary resolution across expanded candidates (handles legacy multi-hop codes)
    pass2_clauses = []
    for cid in candidate_ids:
        pass2_clauses.extend([{"employeeCode": cid}, {"empId": cid}, {"employeeId": cid}])
    matched_emps2 = await db.employees.find({"$or": pass2_clauses}).to_list(10) if pass2_clauses else []
    for me in matched_emps2:
        if me.get("employeeId"):
            candidate_ids.add(str(me["employeeId"]))
        if me.get("employeeCode"):
            candidate_ids.add(str(me["employeeCode"]))

    employee = matched_emps[0] if matched_emps else (matched_emps2[0] if matched_emps2 else None)
    if employee:
        user["employeeId"] = employee.get("employeeId") or user.get("employeeId") or payload.get("employeeId")
        user["employeeCode"] = employee.get("employeeCode") or user.get("employeeCode") or emp_id
    else:
        user.setdefault("employeeId", payload.get("employeeId"))
        user.setdefault("employeeCode", payload.get("employeeCode"))

    # Fetch authoritative employment history data for branch and company
    emp_hist = await db.employee_employment_histories.find_one({
        "employeeId": {"$in": list(candidate_ids)},
        "isCurrent": True,
        "deletedAt": None
    })
    if not emp_hist:
        # Fallback to most recent employment history if isCurrent is not explicitly set
        emp_hist = await db.employee_employment_histories.find_one({
            "employeeId": {"$in": list(candidate_ids)},
            "deletedAt": None
        })

    if emp_hist:
        user["branchId"] = str(emp_hist["branchId"]) if emp_hist.get("branchId") else None
        user["companyId"] = str(emp_hist["companyId"]) if emp_hist.get("companyId") else None
        user["managerId"] = str(emp_hist["managerId"]) if emp_hist.get("managerId") else None
        
    return user


def require_roles(*allowed_roles: str):
    """Legacy role‑based guard – retained for backward compatibility only.
    New code should use ``require_permission`` instead.
    """
    async def _role_guard(user=Depends(get_current_user)):
        user_role = (user.get("role") or "").lower()
        allowed = [r.lower() for r in allowed_roles]
        if user_role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _role_guard


def require_permission(permission_code: str, resource_context_provider: callable | None = None):
    """Permission‑based dependency.
    * ``permission_code`` – canonical permission identifier (e.g. ``"attendance.read"``).
    * ``resource_context_provider`` – optional callable that FastAPI will natively resolve via Depends.
    If omitted, an empty context is used (only GLOBAL permissions succeed).
    """
    if resource_context_provider is None:
        async def _perm_guard_simple(user=Depends(get_current_user)):
            if not await has_permission(user, permission_code, {}):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            return user
        return _perm_guard_simple
    else:
        async def _perm_guard_complex(
            user=Depends(get_current_user),
            rc=Depends(resource_context_provider)
        ):
            if not isinstance(rc, dict):
                rc = {}
            if not await has_permission(user, permission_code, rc):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            return user
        return _perm_guard_complex
