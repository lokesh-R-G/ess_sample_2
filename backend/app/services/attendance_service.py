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
    
def build_daily_summaries(logs):
    grouped = defaultdict(list)

    for log in logs:
        date_key = log["timestamp"].date()
        grouped[(log["empId"], date_key)].append(log["timestamp"])

    summaries = []

    for (empId, date_val), timestamps in grouped.items():
        timestamps.sort()

        in_time = timestamps[0]
        out_time = timestamps[-1]

        work_hours = (out_time - in_time).total_seconds() / 3600 if len(timestamps) > 1 else 0

        if len(timestamps) > 1:
            status = "Present"
        elif len(timestamps) == 1:
            status = "Present (No Out)"
        else:
            status = "Absent"

        summaries.append({
            "empId": empId,
            "date": date_val.isoformat(),
            "inTime": in_time.isoformat(),
            "outTime": out_time.isoformat() if len(timestamps) > 1 else None,
            "workHours": work_hours,
            "status": status
        })

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
    for summary in summaries:
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
        
        current_date = from_date.date()
        end_date = to_date.date()
        
        holidays_cursor = db.holidays.find({}, {"_id": 0, "date": 1, "name": 1})
        holidays_list = await holidays_cursor.to_list(length=None)
        holiday_dates = {h.get("date"): h.get("name") for h in holidays_list if h.get("date")}

        while current_date <= end_date:
            date_str = current_date.isoformat()
            if date_str in record_dict:
                filled_records.append(record_dict[date_str])
            else:
                if current_date.weekday() == 6:
                    status = "weekoff"
                elif date_str in holiday_dates:
                    status = "holiday"
                else:
                    status = "absent"
                    
                filled_records.append({
                    "empId": emp_id,
                    "date": date_str,
                    "status": status,
                    "inTime": None,
                    "outTime": None,
                    "workHours": 0
                })
            current_date += timedelta(days=1)
        return filled_records
        
    return records
