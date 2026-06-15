from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends

from ...db.mongo import get_database
from ...dependencies import get_current_user


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    db = get_database()
    attendance_rows = await db.attendance.find({"empId": current_user["empId"]}).sort("date", 1).to_list(length=None)

    present = sum(1 for row in attendance_rows if row.get("status") == "present")
    absent = sum(1 for row in attendance_rows if row.get("status") == "absent")
    leave = sum(1 for row in attendance_rows if row.get("status") == "leave")
    weekoff = sum(1 for row in attendance_rows if row.get("status") == "weekoff")
    od = sum(1 for row in attendance_rows if row.get("status") == "od")

    trend_by_month: dict[str, int] = Counter()
    for row in attendance_rows:
        date_value = row.get("date")
        if isinstance(date_value, str) and len(date_value) >= 7:
            trend_by_month[date_value[:7]] += 1

    months = list(trend_by_month.keys())
    present_series = list(trend_by_month.values())

    return {
        "employee": {
            "empId": current_user.get("empId"),
            "name": current_user.get("name") or current_user.get("empId"),
            "designation": current_user.get("designation"),
            "branch": current_user.get("branch"),
        },
        "stats": {
            "presentDays": present,
            "absentDays": absent,
            "leaveBalance": 0,
            "currentSalary": 0,
            "workingHours": round(sum((row.get("workedMinutes") or 0) for row in attendance_rows) / 60, 2),
        },
        "attendance": attendance_rows,
        "distribution": [present, leave, absent, weekoff, od],
        "attendanceTrendData": {
            "months": months,
            "present": present_series,
        },
        "notifications": [],
        "holidays": [],
        "leaveBalance": {},
        "upcomingHolidays": [],
    }
