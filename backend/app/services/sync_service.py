from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Optional
import logging

from ..models import SyncResponse
from .attendance_service import build_daily_summaries, upsert_daily_attendance, upsert_raw_logs
from .essl_service import build_essl_client


async def _fetch_transactions(client, from_date: datetime | None = None, to_date: datetime | None = None) -> list[dict]:
    # run blocking SOAP call in thread
    return await asyncio.to_thread(client.fetch_transactions, from_date, to_date)


async def sync_essl_logs(db, from_date: datetime | None = None, to_date: datetime | None = None) -> SyncResponse:
    client = build_essl_client()
    raw_records = await _fetch_transactions(client, from_date=from_date, to_date=to_date)
    sync_batch_id = str(uuid4())

    raw_result = await upsert_raw_logs(db, raw_records, sync_batch_id)
    summaries = build_daily_summaries(raw_records)
    attendance_upserted = await upsert_daily_attendance(db, summaries)

    return SyncResponse(
        rawInserted=raw_result["inserted"],
        rawUpdated=raw_result["updated"],
        attendanceUpserted=attendance_upserted,
        dateRange={
            "fromDate": from_date.isoformat() if from_date else None,
            "toDate": to_date.isoformat() if to_date else None,
        },
    )


async def sync_user(db, emp_id: str, from_date: Optional[datetime] = None, to_date: Optional[datetime] = None) -> dict:
    """Fetch and sync attendance for a single employee. Updates user's dataSyncStatus and lastSyncAt."""
    logger = logging.getLogger("sync_service")
    client = build_essl_client()
    now = datetime.now(timezone.utc)
    try:
        logger.info("Starting sync for empId %s from %s to %s", emp_id, from_date, to_date)
        await db.users.update_one({"empId": emp_id}, {"$set": {"dataSyncStatus": "processing"}})

        # limit fetch window to reasonable bounds
        records = await _fetch_transactions(client, from_date=from_date, to_date=to_date)
        # filter to employee
        user_records = [r for r in records if r.get("empId") == emp_id]

        sync_batch_id = str(uuid4())
        logger.info("Fetched %s raw records for empId %s", len(user_records), emp_id)
        raw_result = await upsert_raw_logs(db, user_records, sync_batch_id)
        summaries = build_daily_summaries(user_records)
        attendance_upserted = await upsert_daily_attendance(db, summaries)

        await db.users.update_one({"empId": emp_id}, {"$set": {"dataSyncStatus": "completed", "lastSyncAt": now}})

        logger.info("Completed sync for empId %s: rawInserted=%s attendanceUpserted=%s", emp_id, raw_result["inserted"], attendance_upserted)

        return {
            "empId": emp_id,
            "rawInserted": raw_result["inserted"],
            "rawUpdated": raw_result["updated"],
            "attendanceUpserted": attendance_upserted,
            "lastSyncAt": now,
        }
    except Exception as exc:
        await db.users.update_one({"empId": emp_id}, {"$set": {"dataSyncStatus": "failed"}})
        logger.exception("Sync failed for empId %s", emp_id)
        raise


async def sync_user_incremental(db, emp_id: str) -> dict:
    user = await db.users.find_one({"empId": emp_id})
    last_sync = user.get("lastSyncAt") if user else None
    if last_sync:
        from_date = last_sync
    else:
        # default incremental window: last 90 days
        from_date = datetime.now(timezone.utc) - timedelta(days=90)
    return await sync_user(db, emp_id, from_date=from_date, to_date=None)


async def sync_all_users_incremental(db) -> list[dict]:
    results = []
    cursor = db.users.find({}, {"empId": 1})
    async for u in cursor:
        emp_id = u.get("empId")
        try:
            res = await sync_user_incremental(db, emp_id)
            results.append(res)
        except Exception:
            # continue on failure
            continue
    return results
