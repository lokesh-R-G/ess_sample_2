from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends

from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.services.attendance_service import infer_attendance_status
from app.services.policy_service import get_attendance_policy
from app.core.datetime_utils import get_current_ist, compare_time_with_policy

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    db = get_database()
    # exclude internal MongoDB _id to keep payload JSON serializable
    attendance_rows = await db.attendance.find({"empId": current_user["empId"]}, {"_id": 0}).sort("date", 1).to_list(length=None)

    present = sum(1 for row in attendance_rows if infer_attendance_status(row) == "present")
    absent = sum(1 for row in attendance_rows if infer_attendance_status(row) == "absent")
    leave = sum(1 for row in attendance_rows if infer_attendance_status(row) == "leave")
    weekoff = sum(1 for row in attendance_rows if infer_attendance_status(row) == "weekoff")
    od = sum(1 for row in attendance_rows if infer_attendance_status(row) == "od")

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
        "attendance": [ {**row, "status": infer_attendance_status(row)} for row in attendance_rows ],
        "distribution": [present, leave, absent, weekoff, od],
        "attendanceTrendData": {
            "months": months,
            "present": present_series,
        },
        "notifications": [],
        "holidays": [],
        "leaveBalance": {},
        "upcomingHolidays": [],
        "alerts": _generate_alerts(attendance_rows, current_user, await get_attendance_policy(db))
    }

def _generate_alerts(attendance_rows: list[dict], user: dict, policy) -> list[dict]:
    alerts = []
    
    # 1. Late & Permission logic based on current month
    now = get_current_ist()
    month_str = now.strftime("%Y-%m")
    today_str = now.strftime("%Y-%m-%d")
    
    # Filter records to current month up to today
    monthly_records = [r for r in attendance_rows if r.get("date", "").startswith(month_str)]
    today_record = next((r for r in monthly_records if r.get("date") == today_str), None)
    
    late_count = sum(1 for r in monthly_records if r.get("lateMinutes", 0) > 0)
    perm_used = sum(r.get("permissionHoursUsed", 0.0) for r in monthly_records)
    total_lop = sum(r.get("lopHours", 0.0) for r in monthly_records)
    
    if late_count >= policy.lateFullDayThreshold:
        alerts.append({"type": "error", "message": f"{late_count} Lates reached. 1 Day salary deduction applied."})
    elif late_count >= policy.lateHalfDayThreshold:
        alerts.append({"type": "error", "message": f"{late_count} Lates reached. Half Day will be deducted."})
        
    if total_lop > 0:
        alerts.append({"type": "warning", "message": f"You currently have {total_lop} accumulated LOP hours."})
        
    if perm_used >= policy.monthlyPermissionHours:
        alerts.append({"type": "error", "message": "Your monthly permission balance has been exhausted."})
    else:
        remaining_mins = int((policy.monthlyPermissionHours - perm_used) * 60)
        alerts.append({"type": "warning", "message": f"Remaining Permission Balance: {remaining_mins} Minutes"})
        
    # Today's context
    if not today_record or (not today_record.get("inTime")):
        # Not punched in yet
        shift_start = policy.shiftStartTime
        diff = compare_time_with_policy(now, shift_start)
        if diff < 0:
            alerts.append({"type": "success", "message": f"Good Morning, Check in before {shift_start}."})
        elif diff <= policy.lateEndMinute:
            alerts.append({"type": "warning", "message": "You have entered the Late Window."})
        elif diff <= policy.latePermissionEndMinute:
            alerts.append({"type": "error", "message": "Late Permission Required."})
            
    if today_record:
        if today_record.get("status") == "holiday":
            alerts.append({"type": "warning", "message": "Today is a Holiday."})
        elif today_record.get("status") == "weekoff":
            alerts.append({"type": "warning", "message": "Today is Weekly Off."})
        elif today_record.get("inTime") and not today_record.get("outTime") and now.hour > 19:
            alerts.append({"type": "warning", "message": "Miss Punch detected."})
            
    return alerts
