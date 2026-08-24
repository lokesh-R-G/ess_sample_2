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

    scope = perm_entry.get("scope", "GLOBAL").upper()
    # Normalise resource context to an empty dict to simplify checks
    rc = resource_context or {}

    # Scope enforcement – fail closed if required keys are missing
    if scope == "SELF":
        if rc.get("empId") != user.get("empId"):
            print("AUTHORIZE FAILED: SELF scope violation", user, rc)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="SELF scope violation")
    elif scope == "TEAM":
        # Expect target employee identifier in context
        target_emp_id = rc.get("empId")
        if not target_emp_id:
            print("AUTHORIZE FAILED: TEAM scope missing target employee", user, rc)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="TEAM scope missing target employee")
        # Load target employee (read‑only)
        db = _get_db()
        target_emp = await db.employees.find_one({"employeeId": target_emp_id})
        if not target_emp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target employee not found")
        manager_id = target_emp.get("managerId")
        if not manager_id or manager_id != user.get("empId"):
            print("TEAM SCOPE VIOLATION:", manager_id, user.get("empId"))
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="TEAM scope violation")
    elif scope == "BRANCH":
        if not rc.get("branchId") or rc.get("branchId") != user.get("branchId"):
            print("BRANCH SCOPE VIOLATION:", rc.get("branchId"), user.get("branchId"))
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="BRANCH scope violation")
    elif scope == "COMPANY":
        if not rc.get("companyId") or rc.get("companyId") != user.get("companyId"):
            print("COMPANY SCOPE VIOLATION:", rc.get("companyId"), user.get("companyId"))
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="COMPANY scope violation")
    elif scope == "GLOBAL":
        # No restriction
        pass
    else:
        # Unknown scope – treat as deny
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unknown scope")

    # If we reach here the user is authorised
    return None

# Convenience wrapper used by dependencies – returns True/False instead of raising.
async def has_permission(user: dict, permission_code: str, resource_context: Dict[str, Any] | None = None) -> bool:
    try:
        await authorize(user, permission_code, resource_context)
        return True
    except HTTPException as exc:
        if exc.status_code == status.HTTP_403_FORBIDDEN:
            return False
        raise
