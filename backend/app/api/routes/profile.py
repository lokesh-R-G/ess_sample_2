from __future__ import annotations

from fastapi import APIRouter, Depends

from ...dependencies import get_current_user


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {
        "empId": current_user.get("empId"),
        "role": current_user.get("role", "Employee"),
        "firstLogin": bool(current_user.get("firstLogin", True)),
        "name": current_user.get("name"),
        "email": current_user.get("email"),
        "phone": current_user.get("phone"),
        "designation": current_user.get("designation"),
        "department": current_user.get("department"),
        "branch": current_user.get("branch"),
        "branchId": current_user.get("branchId"),
        "joiningDate": current_user.get("joiningDate"),
        "reportingTo": current_user.get("reportingTo"),
        "employeeType": current_user.get("employeeType"),
        "address": current_user.get("address"),
        "bankDetails": current_user.get("bankDetails", {}),
        "emergencyContact": current_user.get("emergencyContact", {}),
    }
