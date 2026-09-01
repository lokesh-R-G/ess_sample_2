from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.db.mongo import get_database
from app.db.mongo import get_database
from app.dependencies import get_current_user, require_permission


router = APIRouter(prefix="/deprecated_leave", tags=["leave_deprecated"])


@router.get("/me/")
async def my_leave_requests(current_user=Depends(get_current_user)):
    db = get_database()
    leave_rows = await db.leave_requests.find({"empId": current_user["empId"]}, {"_id": 0}).sort("createdAt", -1).to_list(length=None)
    balance_rows = await db.leave_balances.find_one({"empId": current_user["empId"]}, {"_id": 0})
    return {
        "leaveBalance": balance_rows or {},
        "requests": leave_rows,
        "leaveAnalysisData": [
            len([row for row in leave_rows if row.get("requestType") == "leave"]),
            len([row for row in leave_rows if row.get("requestType") == "od"]),
            len([row for row in leave_rows if row.get("status") == "pending"]),
        ],
    }


@router.post("/me/")
async def create_leave_request(payload: dict, current_user=Depends(get_current_user)):
    db = get_database()
    now = datetime.now(timezone.utc)
    document = {
        "empId": current_user["empId"],
        "requestType": payload.get("requestType", "leave"),
        "leaveType": payload.get("leaveType"),
        "isHalfDay": payload.get("isHalfDay", False),
        "fromDate": payload.get("fromDate"),
        "toDate": payload.get("toDate"),
        "reason": payload.get("reason"),
        "odLocation": payload.get("odLocation"),
        "status": "pending",
        "appliedOn": now.date().isoformat(),
        "createdAt": now,
        "updatedAt": now,
    }
    await db.leave_requests.insert_one(document)
    return {"success": True}

from bson.objectid import ObjectId

@router.get("/pending/")
async def pending_leaves(_admin=Depends(require_permission("leave.approve"))):
    db = get_database()
    cursor = db.leave_requests.find({"status": "pending"})
    requests = await cursor.to_list(length=None)
    for r in requests:
        r["id"] = str(r["_id"])
        del r["_id"]
    return requests

from datetime import timedelta

@router.post("/{req_id}/approve/")
async def approve_leave(req_id: str, _admin=Depends(require_permission("leave.approve"))):
    db = get_database()
    now = datetime.now(timezone.utc)
    
    # fetch the request
    req = await db.leave_requests.find_one({"_id": ObjectId(req_id)})
    if not req:
        return {"error": "Request not found"}

    await db.leave_requests.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": "approved", "updatedAt": now}})
    
    # implement override
    emp_id = req.get("empId")
    from_date_str = req.get("fromDate")
    to_date_str = req.get("toDate")
    req_type = req.get("requestType", "leave") # "leave" or "od"
    
    # Resolve Canonical Employee ID
    emp = await db.employees.find_one({"employeeCode": emp_id})
    canonical_emp_id = emp.get("employeeId") if emp else None

    if canonical_emp_id and from_date_str and to_date_str:
        try:
            current_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
            
            # 1. Create Approval Record
            approval_doc = {
                "employeeId": canonical_emp_id,
                "approvalType": "Leave" if req_type == "leave" else "On Duty",
                "status": "APPROVED",
                "requestData": {
                    "leaveType": req.get("leaveType", "CL"),
                    "isHalfDay": req.get("isHalfDay", False),
                    "fromDate": from_date_str,
                    "toDate": to_date_str,
                    "reason": req.get("reason"),
                    "legacyReqId": req_id
                },
                "createdAt": now,
                "updatedAt": now
            }
            res = await db.approvals.insert_one(approval_doc)
            approval_id = str(res.inserted_id)
            
            # 2. Update Ledger
            from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
            ledger_svc = LeaveLedgerService(db)
            await ledger_svc.commit_approval(approval_id)
            
            # 3. Reprocess Attendance
            from app.services.attendance_service import build_daily_summaries
            # fetch raw punches for the employee within the date range
            # We don't have all the raw punches in this context easily unless we query logs, 
            # but wait, build_daily_summaries takes (db, logs, from_date, to_date).
            # If we pass an empty logs list, it might mark absent! But we need it to process the new approvals.
            # We should query the raw logs for those dates.
            logs_cursor = db.raw_attendance_logs.find({
                "empId": emp_id,
                "timestamp": {
                    "$gte": datetime.combine(current_date, datetime.min.time()),
                    "$lte": datetime.combine(end_date, datetime.max.time())
                }
            })
            logs = await logs_cursor.to_list(length=None)
            
            # Convert target dates to datetime
            from_dt = datetime.combine(current_date, datetime.min.time())
            to_dt = datetime.combine(end_date, datetime.max.time())
            
            await build_daily_summaries(db, logs, from_dt, to_dt)
            
        except Exception as e:
            print("Error processing approval:", e)

    return {"success": True}

@router.post("/{req_id}/reject/")
async def reject_leave(req_id: str, _admin=Depends(require_permission("leave.approve"))):
    db = get_database()
    now = datetime.now(timezone.utc)
    req = await db.leave_requests.find_one({"_id": ObjectId(req_id)})
    if not req:
        return {"error": "Request not found"}

    await db.leave_requests.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": "rejected", "updatedAt": now}})
    
    # 1. Update Approval Record if it exists
    app_doc = await db.approvals.find_one({"requestData.legacyReqId": req_id})
    if app_doc:
        approval_id = str(app_doc["_id"])
        await db.approvals.update_one({"_id": ObjectId(approval_id)}, {"$set": {"status": "REJECTED", "updatedAt": now}})
        
        # 2. Rollback Ledger
        from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
        ledger_svc = LeaveLedgerService(db)
        await ledger_svc.rollback_approval(approval_id)
        
        # 3. Reprocess Attendance
        from app.services.attendance_service import build_daily_summaries
        emp_id = req.get("empId")
        from_date_str = req.get("fromDate")
        to_date_str = req.get("toDate")
        
        if emp_id and from_date_str and to_date_str:
            try:
                current_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
                
                logs_cursor = db.raw_attendance_logs.find({
                    "empId": emp_id,
                    "timestamp": {
                        "$gte": datetime.combine(current_date, datetime.min.time()),
                        "$lte": datetime.combine(end_date, datetime.max.time())
                    }
                })
                logs = await logs_cursor.to_list(length=None)
                
                from_dt = datetime.combine(current_date, datetime.min.time())
                to_dt = datetime.combine(end_date, datetime.max.time())
                
                await build_daily_summaries(db, logs, from_dt, to_dt)
            except Exception as e:
                print("Error reprocessing attendance on reject:", e)
                
    return {"success": True}
