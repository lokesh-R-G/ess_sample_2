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


def build_daily_summaries(records: Iterable[dict]) -> list[dict]:
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

        summaries.append(
            {
                "empId": emp_id,
                "date": attendance_date.isoformat(),
                "firstIn": first_in,
                "lastOut": last_out,
                "punchCount": punch_count,
                "workedMinutes": worked_minutes,
                "status": "present" if punch_count > 0 else "absent",
                "sourceLogFingerprints": [item["fingerprint"] for item in ordered],
                "updatedAt": _utc_now(),
            }
        )

    return summaries


async def upsert_raw_logs(db, records: list[dict], sync_batch_id: str) -> dict[str, int]:
    inserted = 0
    updated = 0

    for record in records:
        document = build_raw_log_document(record, sync_batch_id)
        result = await db.attendance_logs.update_one(
            {"fingerprint": document["fingerprint"]},
            {"$set": document},
            upsert=True,
        )
        if result.upserted_id is not None:
            inserted += 1
        elif result.modified_count > 0:
            updated += 1

    return {"inserted": inserted, "updated": updated}


async def upsert_daily_attendance(db, summaries: list[dict]) -> int:
    upserted = 0
    for summary in summaries:
        result = await db.attendance.update_one(
            {"empId": summary["empId"], "date": summary["date"]},
            {"$set": {**summary, "createdAt": _utc_now()}},
            upsert=True,
        )
        if result.upserted_id is not None or result.modified_count > 0:
            upserted += 1
    return upserted


async def get_attendance_for_employee(db, emp_id: str, from_date: datetime | None = None, to_date: datetime | None = None) -> list[dict]:
    query: dict = {"empId": emp_id}
    if from_date or to_date:
        query["date"] = {}
        if from_date:
            query["date"]["$gte"] = from_date.date().isoformat()
        if to_date:
            query["date"]["$lte"] = to_date.date().isoformat()

    cursor = db.attendance.find(query).sort([("date", 1)])
    return await cursor.to_list(length=None)
