from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.attendance_v2.services.permission_ledger_service import PermissionLedgerService

router = APIRouter(prefix="/permission-ledger", tags=["Permission Ledger"])

@router.get("/me")
async def get_my_ledger(
    db = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    emp_code = user.get("empId")
    if not emp_code:
        raise HTTPException(status_code=401, detail="User has no empId")
        
    employee = await db.employees.find_one({"employeeCode": emp_code})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    emp_uuid = employee.get("employeeId")
    
    # Target month is the current month in IST/UTC (use UTC for simplicity, or current local month)
    # The prompt explicitly wants "month": "2026-08"
    now_utc = datetime.now(timezone.utc)
    month_str = now_utc.strftime("%Y-%m")
    
    ledger_svc = PermissionLedgerService(db)
    
    # Dynamically fetch the current active policy to return limits
    # _get_policy_for_month dynamically resolves the policy for the given month
    policy = await ledger_svc._get_policy_for_month(emp_uuid, month_str)
    
    # Calculate ledger
    ledger_state = await ledger_svc.get_or_calculate_ledger(emp_uuid, month_str)
    
    policy_limits = {}
    if policy:
        policy_limits = {
            "permissionMinutes": policy.get("permissionMinutes", 60),
            "permissionPerMonth": policy.get("permissionPerMonth", 2),
            "monthlyPermissionHours": policy.get("monthlyPermissionHours", 1.0),
            "permissionExcessCarryForward": policy.get("permissionExcessCarryForward", True),
            "permissionLopThresholdMinutes": policy.get("permissionLopThresholdMinutes", 240),
            "permissionLopValue": policy.get("permissionLopValue", 0.5)
        }
        
    return {
        "employeeId": emp_uuid,
        "month": month_str,
        "freeAllowanceMinutes": ledger_state.get("freeAllowanceMinutes", 0.0),
        "consumedMinutes": ledger_state.get("consumedMinutes", 0.0),
        "currentExcessMinutes": ledger_state.get("currentExcessMinutes", 0.0),
        "previousCarriedMinutes": ledger_state.get("previousCarriedMinutes", 0.0),
        "accumulatedExcessMinutes": ledger_state.get("accumulatedExcessMinutes", 0.0),
        "lopGenerated": ledger_state.get("lopGenerated", 0.0),
        "remainingCarriedMinutes": ledger_state.get("remainingCarriedMinutes", 0.0),
        "policyLimits": policy_limits
    }
