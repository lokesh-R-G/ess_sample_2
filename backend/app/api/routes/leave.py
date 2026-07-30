from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.db.mongo import get_database
from app.db.mongo import get_database
from app.dependencies import get_current_user, require_roles


router = APIRouter(prefix="/leave", tags=["leave"])


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
async def pending_leaves(_admin=Depends(require_roles("Admin"))):
    db = get_database()
    cursor = db.leave_requests.find({"status": "pending"})
    requests = await cursor.to_list(length=None)
    for r in requests:
        r["id"] = str(r["_id"])
        del r["_id"]
    return requests

from datetime import timedelta

@router.post("/{req_id}/approve/")
async def approve_leave(req_id: str, _admin=Depends(require_roles("Admin"))):
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
    
    if emp_id and from_date_str and to_date_str:
        try:
            current_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
            while current_date <= end_date:
                date_str = current_date.isoformat()
                await db.attendance.update_one(
                    {"empId": emp_id, "date": date_str},
                    {"$set": {
                        "empId": emp_id,
                        "date": date_str,
                        "status": req_type,
                        "source": "override",
                        "workHours": 0,
                        "inTime": None,
                        "outTime": None,
                        "updatedAt": now
                    }},
                    upsert=True
                )
                current_date += timedelta(days=1)
        except Exception as e:
            print("Error creating override records:", e)

    return {"success": True}

@router.post("/{req_id}/reject/")
async def reject_leave(req_id: str, _admin=Depends(require_roles("Admin"))):
    db = get_database()
    await db.leave_requests.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": "rejected", "updatedAt": datetime.now(timezone.utc)}})
    return {"success": True}
