from __future__ import annotations

import asyncio
from functools import lru_cache
from typing import Dict, List, Any

from fastapi import HTTPException, status

from app.db.mongo import get_database

def _get_db():
    """Return a database instance, respecting FastAPI dependency overrides if set.
    This lazy imports the FastAPI app to avoid circular imports.
    """
    try:
        from importlib import import_module
        fastapi_app = import_module('app.main').app
        override = fastapi_app.dependency_overrides.get(get_database)
        if override:
            return override()
    except Exception:
        pass
    return get_database()

# Simple in‑memory cache for role permissions. In a real system you might add TTL/invalidations.
_ROLE_PERM_CACHE: Dict[str, List[Dict[str, Any]]] = {}

async def _load_role_permissions(role_id: str) -> List[Dict[str, Any]]:
    """Load role_permissions documents for a given canonical roleId.
    Returns a list of dicts with at least ``permissionId`` and ``scope`` fields.
    """
    # Use cached version if present
    if role_id in _ROLE_PERM_CACHE:
        return _ROLE_PERM_CACHE[role_id]
    db = _get_db()
    cursor = db.role_permissions.find({"roleId": role_id})
    perms = await cursor.to_list(length=None)
    # Cache the result for the lifetime of the process
    _ROLE_PERM_CACHE[role_id] = perms
    return perms

async def authorize(user: dict, permission_code: str, resource_context: Dict[str, Any] | None = None) -> None:
    """Central authorisation entry point.

    * ``user`` – dict returned by ``get_current_user`` (must contain ``roleId``).
    * ``permission_code`` – the canonical permission identifier (e.g. ``"attendance.read"``).
    * ``resource_context`` – optional dict describing the target resource. Keys may include
      ``empId``, ``branchId``, ``companyId`` etc. Missing keys cause a *fail‑closed* denial.

    Raises ``HTTPException(403)`` when the user is not authorised.
    """
    role_id = user.get("roleId")
    if not role_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing roleId")

    perms = await _load_role_permissions(role_id)
    # Find the permission entry for the requested code
    perm_entry = next((p for p in perms if p.get("permissionId") == permission_code), None)
    if not perm_entry:
        print("AUTHORIZE FAILED: Permission not granted", role_id, permission_code)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission not granted")

    scopes = perm_entry.get("scopes", [])
    if not scopes and "scope" in perm_entry:
        scopes = [perm_entry.get("scope")]
        
    rc = resource_context or {}
    
    for scope in scopes:
        scope = scope.upper()
        try:
            if scope == "SELF":
                if rc.get("empId") != user.get("empId"):
                    continue
                return None
            elif scope == "TEAM":
                # TEAM scope needs the internal employeeId to query histories
                target_employee_id = rc.get("employeeId")
                
                # If it's missing from context, we must resolve it via the canonical empId
                if not target_employee_id:
                    target_emp_id = rc.get("empId")
                    if not target_emp_id:
                        continue
                    db = _get_db()
                    target_emp_doc = await db.employees.find_one({"$or": [{"employeeCode": target_emp_id}, {"empId": target_emp_id}]})
                    if target_emp_doc:
                        target_employee_id = target_emp_doc.get("employeeId")
                    else:
                        target_employee_id = target_emp_id # fallback to treating it as internal id

                if not target_employee_id:
                    continue
                    
                db = _get_db()
                emp_hist = await db.employee_employment_histories.find_one({
                    "employeeId": target_employee_id,
                    "isCurrent": True,
                    "deletedAt": None
                })
                if not emp_hist:
                    # No authoritative history record — deny TEAM (fail-closed).
                    print(f"AUTHORIZE TEAM DENIED: no active employment history for {target_employee_id}")
                    continue
                manager_id = emp_hist.get("managerId")
                if manager_id is None:
                    # managerId is explicitly null → employee is their own effective manager.
                    manager_id = target_employee_id
                
                # manager_id from DB could match either the caller's internal employeeId or canonical empId
                if manager_id in (user.get("employeeId"), user.get("empId")):
                    return None
                # caller is not the effective manager → this scope fails, try next.
            elif scope == "BRANCH":
                if rc.get("branchId") and rc.get("branchId") == user.get("branchId"):
                    return None
            elif scope == "COMPANY":
                if rc.get("companyId") and rc.get("companyId") == user.get("companyId"):
                    return None
            elif scope == "GLOBAL":
                return None
        except Exception as e:
            print(f"Error evaluating scope {scope}: {e}")
            continue

    print("AUTHORIZE FAILED: All scopes failed", role_id, permission_code, scopes, user, rc)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission not granted or scope violation")


# Convenience wrapper used by dependencies – returns True/False instead of raising.
async def has_permission(user: dict, permission_code: str, resource_context: Dict[str, Any] | None = None) -> bool:
    try:
        await authorize(user, permission_code, resource_context)
        return True
    except HTTPException as exc:
        if exc.status_code == status.HTTP_403_FORBIDDEN:
            return False
        raise
