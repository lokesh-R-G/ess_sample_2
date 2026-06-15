from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ...db.mongo import get_database
from ...dependencies import get_current_user


router = APIRouter(prefix="/leave", tags=["leave"])


@router.get("/me")
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


@router.post("/me")
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
