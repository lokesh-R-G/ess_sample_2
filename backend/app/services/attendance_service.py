from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone
from hashlib import sha256
from typing import Iterable


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_fingerprint(emp_id: str, timestamp: datetime, raw_payload: str) -> str:
    payload = f"{emp_id}|{timestamp.isoformat()}|{raw_payload}".encode("utf-8")
    return sha256(payload).hexdigest()


def build_raw_log_document(record: dict, sync_batch_id: str) -> dict:
    return {
        "empId": record["empId"],
        "timestamp": record["timestamp"],
        "rawPayload": record["rawPayload"],
        "source": record.get("source", "essl"),
        "fingerprint": record["fingerprint"],
        "syncBatchId": sync_batch_id,
        "createdAt": _utc_now(),
        "updatedAt": _utc_now(),
    }


'''def build_daily_summaries(records: Iterable[dict]) -> list[dict]:
    grouped: dict[tuple[str, date], list[dict]] = defaultdict(list)

    for record in records:
        timestamp = record["timestamp"]
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        grouped[(record["empId"], timestamp.date())].append({**record, "timestamp": timestamp})

    summaries: list[dict] = []
    for (emp_id, attendance_date), items in grouped.items():
        ordered = sorted(items, key=lambda item: item["timestamp"])
        first_in = ordered[0]["timestamp"] if ordered else None
        last_out = ordered[-1]["timestamp"] if ordered else None
        punch_count = len(ordered)
        worked_minutes = 0
        if first_in and last_out and punch_count > 1:
            worked_minutes = max(0, int((last_out - first_in).total_seconds() // 60))

        status = "present" if punch_count > 1 else "absent"

        summaries.append(
            {
                "empId": emp_id,
                "date": attendance_date.isoformat(),
                "firstIn": first_in,
                "lastOut": last_out,
                "punchCount": punch_count,
                "workedMinutes": worked_minutes,
                "status": status,
                "sourceLogFingerprints": [item["fingerprint"] for item in ordered],
                "updatedAt": _utc_now(),'''
from datetime import date, datetime, timezone, timedelta
from app.services.policy_service import get_attendance_policy
from app.services.policy_engine import PolicyEngine
from app.core.datetime_utils import to_utc, to_ist, get_current_ist

from app.services.attendance_context_resolver import AttendanceContextResolver

async def build_daily_summaries(db, logs, from_date: datetime | None = None, to_date: datetime | None = None):
    grouped = defaultdict(list)
    import pytz
    from datetime import timedelta
    ist = pytz.timezone("Asia/Kolkata")
    
    for log in logs:
        if isinstance(log["timestamp"], str):
            log["timestamp"] = datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
        elif getattr(log["timestamp"], "tzinfo", None) is None:
            log["timestamp"] = log["timestamp"].replace(tzinfo=timezone.utc).astimezone(ist)
        else:
            log["timestamp"] = log["timestamp"].astimezone(ist)
            
        date_key = log["timestamp"].date()
        grouped[(log["empId"], date_key)].append(log)

    # Determine processing boundaries
    emp_ids = list(set([k[0] for k in grouped.keys()]))
    if not emp_ids:
        # If no logs but we need to process, we need emp_ids. Since we don't have them, return []
        return []
        
    dates_in_logs = [k[1] for k in grouped.keys()]
    process_from = from_date.date() if from_date else min(dates_in_logs)
    process_to = to_date.date() if to_date else max(dates_in_logs)

    resolver = AttendanceContextResolver(db)
    
    # Pre-fetch monthly aggregates for this batch
    months = set()
    d = process_from
    while d <= process_to:
        months.add(d.strftime("%Y-%m"))
        d += timedelta(days=1)
    
    monthly_records = []
    if emp_ids and months:
        month_regex = "^(" + "|".join(list(months)) + ")"
        cursor = db.attendance.find({
            "empId": {"$in": emp_ids},
            "date": {"$regex": month_regex}
        })
        monthly_records = await cursor.to_list(length=None)

    summaries = []

    for empId in emp_ids:
        current_date = process_from
        while current_date <= process_to:
            items = grouped.get((empId, current_date), [])
            
            ctx = await resolver.resolve_context(empId, current_date)
            if not ctx or not ctx.get("policy"):
                current_date += timedelta(days=1)
                continue

            engine = PolicyEngine(
                shift=ctx.get("shift"),
                policy=ctx.get("policy"),
                holiday_dates=ctx.get("holidayDates"),
                today_schedule=ctx.get("todaySchedule"),
                monthly_records=monthly_records,
                approved_requests=ctx.get("approvedRequests", [])
            )

            in_time = None
            out_time = None
            fingerprints = []
            
            if items:
                items.sort(key=lambda x: x["timestamp"])
                timestamps = [x["timestamp"] for x in items]
                fingerprints = [x.get("fingerprint") for x in items if "fingerprint" in x]
                in_time = timestamps[0]
                out_time = timestamps[-1] if len(timestamps) > 1 else None

            # Phase 6 & 8 Integration: Evaluate every day, even without punches
            metrics = engine.evaluate_attendance(empId, datetime.combine(current_date, datetime.min.time()), in_time, out_time)

            work_hours = (out_time - in_time).total_seconds() / 3600 if (in_time and out_time and len(items) > 1) else 0

            # Phase 7: Snapshot integration
            summary = {
                "empId": empId,
                "date": current_date.isoformat(),
                "shiftId": str(getattr(ctx.get("shift"), "id", getattr(ctx.get("shift"), "_id", None))) if ctx.get("shift") else None,
                "attendancePolicyId": str(getattr(ctx.get("policy"), "id", getattr(ctx.get("policy"), "_id", None))) if ctx.get("policy") else None,
                "weeklyOffPolicyId": str(getattr(ctx.get("weeklyOffPolicy"), "id", getattr(ctx.get("weeklyOffPolicy"), "_id", None))) if ctx.get("weeklyOffPolicy") else None,
                "holidayCalendarId": ctx.get("holidayCalendar"),
                "todaySchedule": ctx.get("todaySchedule"),
                "inTime": in_time.isoformat() if in_time else None,
                "outTime": out_time.isoformat() if out_time else None,
                "workHours": work_hours,
                "status": metrics["status"],
                "lateMinutes": metrics.get("lateMinutes", 0),
                "lateCount": metrics.get("lateCount", 0),
                "permissionHoursUsed": metrics.get("permissionHoursUsed", 0.0),
                "permissionHoursExceeded": metrics.get("permissionHoursExceeded", 0.0),
                "lopHours": metrics.get("lopHours", 0.0),
                "halfDayCount": metrics.get("halfDayCount", 0.0),
                "sourceLogFingerprints": fingerprints,
                "engineVersion": "v0.2",
                "processedAt": datetime.now(timezone.utc).isoformat(),
                "timezone": "Asia/Kolkata"
            }
            summaries.append(summary)
            current_date += timedelta(days=1)

    return summaries

def infer_attendance_status(record: dict) -> str:
    status = record.get("status")
    if status in {"present", "absent", "leave", "weekoff", "od", "partial"}:
        return status

    # check common timestamp fields used by daily summaries
    if record.get("firstIn") and record.get("lastOut"):
        return "present"

    # legacy/raw payload fields
    if record.get("inTime") and record.get("outTime"):
        return "present"

    # fallback to punch count
    if record.get("punchCount") and record.get("punchCount") > 1:
        return "present"

    return "absent"


async def upsert_raw_logs(db, records: list[dict], sync_batch_id: str) -> dict[str, int]:
    inserted = 0
    updated = 0

    for record in records:
        document = build_raw_log_document(record, sync_batch_id)
        try:
            result = await db.attendance_logs.update_one(
                {"fingerprint": document["fingerprint"]},
                {"$set": document},
                upsert=True,
            )
            if result.upserted_id is not None:
                inserted += 1
            elif result.modified_count > 0:
                updated += 1
        except Exception as e:
            # log but continue on duplicate or other errors
            pass

    print(f"   Raw logs: inserted={inserted}, updated={updated}")
    return {"inserted": inserted, "updated": updated}


async def upsert_daily_attendance(db, summaries: list[dict]) -> int:
    upserted = 0
    
    # get existing overrides for the dates in summaries
    dates = [s["date"] for s in summaries]
    emp_ids = list(set([s["empId"] for s in summaries]))
    
    overrides_cursor = db.attendance.find({"empId": {"$in": emp_ids}, "date": {"$in": dates}, "source": "override"})
    overrides = await overrides_cursor.to_list(length=None)
    override_set = {(o["empId"], o["date"]) for o in overrides}

    for summary in summaries:
        if (summary["empId"], summary["date"]) in override_set:
            continue # skip overridden days
            
        try:
            result = await db.attendance.update_one(
                {"empId": summary["empId"], "date": summary["date"]},
                {"$set": {**summary, "createdAt": _utc_now()}},
                upsert=True,
            )
            if result.upserted_id is not None or result.modified_count > 0:
                upserted += 1
        except Exception as e:
            # log but continue on errors
            pass
    
    print(f"   Daily attendance: upserted={upserted}")
    return upserted


async def get_attendance_for_employee(db, emp_id: str, from_date: datetime | None = None, to_date: datetime | None = None) -> list[dict]:
    query: dict = {"empId": emp_id}
    if from_date or to_date:
        query["date"] = {}
        if from_date:
            query["date"]["$gte"] = from_date.date().isoformat()
        if to_date:
            query["date"]["$lte"] = to_date.date().isoformat()

    # exclude MongoDB internal ObjectId to keep response JSON-serializable
    cursor = db.attendance.find(query, {"_id": 0}).sort([("date", 1)])
    records = await cursor.to_list(length=None)

    if from_date and to_date:
        record_dict = {r["date"]: r for r in records}
        filled_records = []
        
        current_date_ist = to_ist(from_date).date()
        end_date_ist = to_ist(to_date).date()
        today_ist = get_current_ist().date()
        end_date_ist = min(end_date_ist, today_ist)
        
        resolver = AttendanceContextResolver(db)
        # We can resolve once for the from_date (assuming same year)
        ctx = await resolver.resolve_context(emp_id, from_date.date())
        holiday_dates = []
        if ctx and ctx.get("holidayDates"):
            holiday_dates = ctx["holidayDates"]
            
        weekly_off_policy = None
        if ctx and "weeklyOffPolicy" in ctx:
            weekly_off_policy = ctx["weeklyOffPolicy"]
            
        holiday_dict = {}
        for hd in holiday_dates:
            d_val = hd.get("holidayDate") if isinstance(hd, dict) else getattr(hd, "holidayDate", None)
            name_val = hd.get("holidayName") if isinstance(hd, dict) else getattr(hd, "holidayName", None)
            if d_val:
                holiday_dict[str(d_val)] = name_val

        while current_date_ist <= end_date_ist:
            date_str = current_date_ist.isoformat()
            if date_str in record_dict:
                rec = record_dict[date_str]
                # Apply priority logic
                if rec.get("source") != "override":
                    today_sched = resolver.resolve_today_schedule(weekly_off_policy, current_date_ist)
                    if today_sched.get("dayType") == "WEEKOFF":
                        rec["status"] = "Week Off Worked" if rec.get("inTime") else "Week Off"
                    elif date_str in holiday_dict:
                        rec["status"] = "Holiday"
                filled_records.append(rec)
            else:
                today_sched = resolver.resolve_today_schedule(weekly_off_policy, current_date_ist)
                if today_sched.get("dayType") == "WEEKOFF":
                    status = "Week Off"
                elif date_str in holiday_dict:
                    status = "Holiday"
                else:
                    status = "Absent"
                    
                filled_records.append({
                    "empId": emp_id,
                    "date": date_str,
                    "status": status,
                    "inTime": None,
                    "outTime": None,
                    "workHours": 0,
                    "lateMinutes": 0,
                    "lateCount": 0,
                    "permissionHoursUsed": 0.0,
                    "lopHours": 0.0,
                    "halfDayCount": 0.0
                })
            current_date_ist += timedelta(days=1)
        return filled_records
        
    return records
