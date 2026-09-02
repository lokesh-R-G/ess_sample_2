from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService

router = APIRouter(prefix="/v2/leave", tags=["leave_v2"])

@router.get("/balances")
async def get_leave_balances(current_user=Depends(get_current_user)):
    db = get_database()
    emp_id = current_user.get("employeeId")
    if not emp_id:
        emp_code_tok = current_user.get("empId")
        if emp_code_tok:
            emp = await db.employees.find_one({"employeeCode": emp_code_tok})
            if emp:
                emp_id = emp.get("employeeId")
                
    if not emp_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Could not resolve employee ID")
        
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
