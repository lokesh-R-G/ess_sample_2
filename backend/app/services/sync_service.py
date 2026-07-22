from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Optional
import logging
from pymongo.errors import DuplicateKeyError

from ..models import SyncResponse
from .attendance_service import build_daily_summaries, upsert_daily_attendance, upsert_raw_logs
from .essl_service import build_essl_client


class DictAttrWrapper:
    def __init__(self, data: dict | None):
        self._data = data or {}

    @property
    def empId(self) -> str:
        return self._data.get("empId", "")

    @property
    def lastSyncAt(self) -> datetime | None:
        return self._data.get("lastSyncAt")

    @lastSyncAt.setter
    def lastSyncAt(self, value: datetime | None) -> None:
        self._data["lastSyncAt"] = value


async def _fetch_transactions(client, from_date: datetime | None = None, to_date: datetime | None = None) -> list[dict]:
    # run blocking SOAP call in thread
    return await asyncio.to_thread(client.fetch_transactions, from_date, to_date)


async def sync_essl_logs(db, from_date: datetime | None = None, to_date: datetime | None = None) -> SyncResponse:
    client = build_essl_client()
    raw_records = await _fetch_transactions(client, from_date=from_date, to_date=to_date)
    if to_date is None:
        to_date = datetime.now(timezone.utc)   
    sync_batch_id = str(uuid4())

    raw_result = await upsert_raw_logs(db, raw_records, sync_batch_id)
    summaries = await build_daily_summaries(db, raw_records)
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
    try:
        logger.info("Starting sync for empId %s from %s to %s", emp_id, from_date, to_date)
        print(f"📋 Syncing employee {emp_id} from {from_date} to {to_date}")
        await db.users.update_one({"empId": emp_id}, {"$set": {"dataSyncStatus": "processing"}})

        # limit fetch window to reasonable bounds
        records = await _fetch_transactions(client, from_date=from_date, to_date=to_date)
        # filter to employee
        parsed_data = [r for r in records if r.get("empId") == emp_id]

        print("📦 Parsed records:", len(parsed_data))
        logger.info("Fetched %s raw records for empId %s", len(parsed_data), emp_id)

        from pymongo.errors import DuplicateKeyError
        from .attendance_service import build_raw_log_document

        sync_batch_id = str(uuid4())
        inserted = 0
        for record in parsed_data:
            doc = build_raw_log_document(record, sync_batch_id)
            try:
                await db.attendance_logs.insert_one(doc)
                inserted += 1
            except DuplicateKeyError:
                pass

        print("✅ Records inserted into DB")

        summaries = await build_daily_summaries(db, parsed_data)
        #attendance_upserted = await upsert_daily_attendance(db, summaries)
        if not summaries:
            summaries = []

        attendance_upserted = await upsert_daily_attendance(db, summaries)
        raw_user = await db.users.find_one({"empId": emp_id})
        user = DictAttrWrapper(raw_user)
        user.lastSyncAt = datetime.now(timezone.utc)
        await db.users.update_one({"empId": emp_id}, {"$set": {"dataSyncStatus": "completed", "lastSyncAt": user.lastSyncAt}})
        print(f"⏰ Updated lastSyncAt: {user.lastSyncAt}")

        logger.info("Completed sync for empId %s: rawInserted=%s attendanceUpserted=%s", emp_id, inserted, attendance_upserted)

        return {
            "empId": emp_id,
            "rawInserted": inserted,
            "rawUpdated": 0,
            "attendanceUpserted": attendance_upserted,
            "lastSyncAt": user.lastSyncAt,
        }
    except Exception as exc:
        await db.users.update_one({"empId": emp_id}, {"$set": {"dataSyncStatus": "failed"}})
        logger.exception("Sync failed for empId %s", emp_id)
        print(f"❌ Sync failed for {emp_id}: {str(exc)}")
        raise


async def sync_user_incremental(db, emp_id: str) -> dict:
    raw_user = await db.users.find_one({"empId": emp_id})
    user = DictAttrWrapper(raw_user)

    '''if not user.lastSyncAt:
        from_date = datetime.now(timezone.utc) - timedelta(days=90)
    else:
        from_date = user.lastSyncAt - timedelta(minutes=5)

    return await sync_user(db, emp_id, from_date=from_date, to_date=None)'''
    now = datetime.now(timezone.utc)
    if not user.lastSyncAt or user.lastSyncAt > now:
        print("⚠️ Invalid lastSyncAt detected, resetting to last 30 days")
        from_date = now - timedelta(days=30)
    else:
        from_date = user.lastSyncAt - timedelta(minutes=5)
    return await sync_user(db, emp_id, from_date=from_date, to_date=now)


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
