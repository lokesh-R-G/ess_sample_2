from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime, timezone
from app.db.mongo import get_database
from app.authz import authorize, AuthorizedScope
from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService

router = APIRouter(prefix="/v2/leave", tags=["leave_v2"])

@router.get("/balances")
async def get_leave_balances(
    employeeId: str = Query(None),
    authz: AuthorizedScope = Depends(authorize("leave.read"))
):
    db = get_database()
    
    target_emp_id = employeeId or authz.employee_id
    if not target_emp_id:
        raise HTTPException(status_code=400, detail="Could not resolve employee ID")
        
    await authz.validate_resource_employee(target_emp_id)
    emp_id = target_emp_id
        
    year = datetime.now(timezone.utc).year
    
    # We need employeeCode for initialization
    emp = await db.employees.find_one({"employeeId": emp_id})
    emp_code = emp.get("employeeCode", "UNKNOWN") if emp else "UNKNOWN"
    
    ledger_svc = LeaveLedgerService(db)
    
    now = datetime.now(timezone.utc)
    target_date = now
    query = {
        "deletedAt": None,
        "effectiveFrom": {"$lte": target_date},
        "$or": [
            {"effectiveTo": None},
            {"effectiveTo": {"$gt": target_date}}
        ]
    }
    
    docs = await db.leave_policies.find(query).sort([("version", -1)]).to_list(length=1)
    if not docs:
        docs = await db.leave_policies.find({"deletedAt": None, "isCurrent": True}).sort([("version", -1)]).to_list(length=1)
        
    leave_types = []
    if docs:
        policy = docs[0]
        leave_types = [t.get("code") for t in policy.get("leaveTypes", []) if t.get("enabled", True)]
        
    balances = {}
    for lt in leave_types:
        ledger = await ledger_svc.get_or_create_ledger(emp_id, emp_code, year, lt)
        balances[lt] = {
            "total": ledger.get("openingBalance", 0.0),
            "used": ledger.get("consumed", 0.0),
            "balance": ledger.get("availableBalance", 0.0)
        }
        
    return balances
