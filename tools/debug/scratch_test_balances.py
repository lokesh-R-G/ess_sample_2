import asyncio
from httpx import AsyncClient

from app.db.mongo import get_database
from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService

async def main():
    db = get_database()
    emp = await db.employees.find_one({"status": "Active"})
    if not emp: return
    
    emp_id = emp["employeeId"]
    emp_code = emp.get("employeeCode", "UNKNOWN")
    
    ledger_svc = LeaveLedgerService(db)
    
    # Let's mock a pending approval and commit it
    from bson import ObjectId
    app_id = ObjectId()
    app_doc = {
        "_id": app_id,
        "employeeId": emp_id,
        "approvalType": "Leave",
        "status": "APPROVED",
        "requestData": {
            "leaveType": "tes_CL",
            "fromDate": "2026-08-13",
            "toDate": "2026-08-13"
        }
    }
    await db.approvals.insert_one(app_doc)
    
    print("Committing approval...")
    try:
        await ledger_svc.commit_approval(str(app_id))
        print("Success.")
    except Exception as e:
        print("Error in commit_approval:", e)
        
    ledgers = await db.leave_ledgers.find({"employeeId": emp_id, "calendarYear": 2026}).to_list(length=10)
    for l in ledgers:
        print(f"{l['leaveType']}: available={l.get('availableBalance')} consumed={l.get('consumed')} opening={l.get('openingBalance')} allocations={l.get('allocations')}")

        
if __name__ == "__main__":
    asyncio.run(main())
