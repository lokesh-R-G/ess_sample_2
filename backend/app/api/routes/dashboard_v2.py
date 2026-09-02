from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.core.datetime_utils import get_current_ist, to_utc

router = APIRouter(prefix="/dashboard", tags=["dashboard_v2"])


@router.get("/me/")
async def get_dashboard_me(current_user=Depends(get_current_user)):
    db = get_database()

    # 1. Employee Identity (resolve from UUID, use code/name for display)
    emp_uuid = current_user.get("employeeId")
    emp_code_jwt = current_user.get("empId")

    emp_doc = None
    if emp_uuid:
        emp_doc = await db.employees.find_one({"employeeId": emp_uuid})
    elif emp_code_jwt:
        emp_doc = await db.employees.find_one({"employeeCode": emp_code_jwt})
        if emp_doc:
            emp_uuid = emp_doc.get("employeeId")

    if not emp_doc or not emp_uuid:
        raise HTTPException(status_code=400, detail="Could not resolve V2 employee record")

    employee_code = emp_doc.get("employeeCode", "UNKNOWN")
    first_name = emp_doc.get("firstName", "")
    last_name = emp_doc.get("lastName", "")
    employee_name = f"{first_name} {last_name}".strip() or employee_code

    now = get_current_ist()
    first_day_of_month_str = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d")
    today_str = now.strftime("%Y-%m-%d")
    now_utc = to_utc(now)

    # 2. Attendance Statistics (Exclusively from persisted V2 records)
    # The dashboard MUST NOT infer, recalculate, or default absent based on null punches.
    attendance_cursor = db.attendance.find({
        "employeeId": emp_uuid,
        "date": {"$gte": first_day_of_month_str, "$lte": today_str}
    })
    attendance_records = await attendance_cursor.to_list(length=None)

    present = 0
    absent = 0
    leave = 0
    weekoff = 0
    od = 0
    holiday = 0
    half_day = 0
    late = 0
    lop = 0

    processed_records = []
    trend_by_month: dict[str, int] = Counter()

    for r in attendance_records:
        st = r.get("status", "").lower()
        if "present" in st:
            present += 1
            if r.get("date"):
                trend_by_month[r["date"][:7]] += 1
        elif st == "absent":
            absent += 1
        elif st == "leave":
            leave += 1
        elif "week off" in st or st == "weekoff":
            weekoff += 1
        elif st == "od" or st == "on duty":
            od += 1
        elif st == "holiday":
            holiday += 1
        elif "half day" in st:
            half_day += 1

        if r.get("lateMinutes", 0) > 0 or r.get("lateFlag"):
            late += 1

        # Calculate LOP (includes leaveLopDays or lopDays)
        # Note: If status="Leave" and leaveLopDays=1, it is counted as Leave=1 and LOP=1, not Absent.
        lop_days = r.get("leaveLopDays", 0) + r.get("lopDays", 0)
        lop_hours = r.get("lopHours", 0)
        if lop_days > 0 or lop_hours > 0:
            lop += 1

        processed_records.append(r)

    months = list(trend_by_month.keys())
    present_series = list(trend_by_month.values())

    # 3. Leave Balance (Exclusively from V2 leave_ledgers and active policy)
    # Get active policy to determine enabled leave types
    policy_query = {
        "deletedAt": None,
        "effectiveFrom": {"$lte": now_utc},
        "$or": [
            {"effectiveTo": None},
            {"effectiveTo": {"$gt": now_utc}}
        ]
    }
    docs = await db.leave_policies.find(policy_query).sort([("version", -1)]).to_list(length=1)
    
    leave_types = []
    if docs:
        policy = docs[0]
        leave_types = [t.get("code") for t in policy.get("leaveTypes", []) if t.get("enabled", True)]
    else:
        # Fallback to query distinct from ledgers if no policy
        leave_types = await db.leave_ledgers.distinct("leaveType", {"employeeId": emp_uuid, "calendarYear": now.year})

    balances = {}
    total_leave_balance = 0.0

    if leave_types:
        ledger_cursor = db.leave_ledgers.find({
            "employeeId": emp_uuid,
            "calendarYear": now.year,
            "leaveType": {"$in": leave_types}
        })
        ledgers = await ledger_cursor.to_list(length=None)
        
        for lt in leave_types:
            l = next((x for x in ledgers if x.get("leaveType") == lt), None)
            if l:
                balances[lt] = {
                    "total": l.get("openingBalance", 0.0),
                    "used": l.get("consumed", 0.0),
                    "balance": l.get("availableBalance", 0.0)
                }
                total_leave_balance += l.get("availableBalance", 0.0)
            else:
                balances[lt] = {"total": 0.0, "used": 0.0, "balance": 0.0}

    # 4. Approvals (Exclusively from V2 approvals collection)
    pending_approvals = await db.approvals.count_documents({
        "employeeId": emp_uuid,
        "status": "PENDING"
    })

    # Serialize object IDs for JSON
    from app.core.serialize import serialize_mongo_doc
    processed_records = serialize_mongo_doc(processed_records)

    return {
        "employee": {
            "employeeId": emp_uuid,
            "employeeCode": employee_code,
            "employeeName": employee_name,
            "designation": emp_doc.get("designation"),
            "branch": emp_doc.get("branchId") or emp_doc.get("branch"),
        },
        "stats": {
            "presentDays": present,
            "absentDays": absent,
            "leaveBalance": total_leave_balance,
            "currentSalary": 0,
            "workingHours": round(sum((row.get("workHours") or 0) for row in processed_records), 2),
            "pendingApprovals": pending_approvals,
            "late": late,
            "lop": lop
        },
        "attendance": processed_records,
        "distribution": [present, leave, absent, weekoff, od, holiday, half_day],
        "attendanceTrendData": {
            "months": months,
            "present": present_series,
        },
        "notifications": [],
        "holidays": [],
        "leaveBalance": balances,
        "upcomingHolidays": [],
        "alerts": []
    }
