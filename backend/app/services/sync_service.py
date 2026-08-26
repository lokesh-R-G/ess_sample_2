from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Optional
import logging
from pymongo.errors import DuplicateKeyError

from app.models import SyncResponse
from app.services.attendance_service import upsert_raw_logs
from app.attendance_v2.services.dirty_queue_service import DirtyQueueService
from app.services.essl_service import build_essl_client


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


async def sync_essl_machine(db, machine: dict, fallback_from_date: datetime | None = None, fallback_to_date: datetime | None = None) -> dict:
    logger = logging.getLogger("sync_service")
    machine_id = str(machine["_id"])
    serial_number = machine.get("serialNumber")
    
    if not serial_number:
        logger.error(f"Machine {machine_id} has no serial number. Skipping.")
        return {"machineId": machine_id, "status": "FAILED", "error": "No serial number"}

    # Set processing lock
    await db.essl_machines.update_one(
        {"_id": machine["_id"]}, 
        {"$set": {"syncStatus": "PROCESSING", "updatedAt": datetime.now(timezone.utc)}}
    )

    try:
        client = build_essl_client(serial_number)
        
        # Cursor logic
        now = datetime.now(timezone.utc)
        to_date = fallback_to_date or now
        
        last_success = machine.get("lastSuccessfulSyncAt")
        if last_success:
            if last_success.tzinfo is None:
                last_success = last_success.replace(tzinfo=timezone.utc)
            else:
                last_success = last_success.astimezone(timezone.utc)
                
        # If user explicitly requested a backfill date, use it. Otherwise rely on cursor.
        if fallback_from_date:
            from_date = fallback_from_date
        elif last_success and last_success <= now:
            # Re-fetch the last 15 minutes to handle clock skew / delayed writes
            from_date = last_success - timedelta(minutes=15)
        else:
            from_date = now - timedelta(days=1)
            
        logger.info(f"Syncing machine {serial_number} from {from_date} to {to_date}")

        raw_records = await _fetch_transactions(client, from_date=from_date, to_date=to_date)
        
        # Ensure machineId and serialNumber are injected (parse_essl_payload does this now, but ensure here)
        for r in raw_records:
            r["machineId"] = machine_id
            r["serialNumber"] = serial_number

        sync_batch_id = str(uuid4())
        raw_result = await upsert_raw_logs(db, raw_records, sync_batch_id)
        
        # Extract unique empIds and push to Dirty Queue
        emp_ids = list(set([r.get("empId") for r in raw_records if r.get("empId")]))
        dirty_queue = DirtyQueueService(db)
        
        fd_iso = from_date.isoformat()
        td_iso = to_date.isoformat()
        
        for emp_code in emp_ids:
            emp = await db.employees.find_one({"employeeCode": emp_code})
            if not emp:
                continue
                
            await dirty_queue.push(
                employee_id=emp["employeeId"],
                employee_code=emp_code,
                from_date=fd_iso,
                to_date=td_iso,
                reason="eSSL Multi-Machine Sync received",
                trigger="ESSL_SYNC"
            )

        # Advance cursor only on success
        await db.essl_machines.update_one(
            {"_id": machine["_id"]},
            {"$set": {
                "syncStatus": "IDLE", 
                "lastSuccessfulSyncAt": to_date,
                "lastSyncAt": now,
                "lastSyncError": None,
                "updatedAt": now
            }}
        )
        
        return {
            "machineId": machine_id,
            "status": "SUCCESS",
            "rawInserted": raw_result.get("inserted", 0),
            "rawUpdated": raw_result.get("modified", 0),
            "rawMatched": raw_result.get("matched_existing", 0),
        }

    except Exception as e:
        logger.error(f"Failed syncing machine {serial_number}: {e}")
        now = datetime.now(timezone.utc)
        await db.essl_machines.update_one(
            {"_id": machine["_id"]},
            {"$set": {
                "syncStatus": "FAILED", 
                "lastSyncError": str(e),
                "lastSyncAt": now,
                "updatedAt": now
            }}
        )
        return {"machineId": machine_id, "status": "FAILED", "error": str(e)}


async def sync_essl_logs(db, from_date: datetime | None = None, to_date: datetime | None = None) -> SyncResponse:
    logger = logging.getLogger("sync_service")
    
    # 1. Fetch all active machines
    cursor = db.essl_machines.find({"status": "Active"})
    machines = await cursor.to_list(length=None)
    
    if not machines:
        logger.warning("No active ESSL machines found in db.essl_machines")
        return SyncResponse(rawInserted=0, rawUpdated=0, rawMatched=0, attendanceUpserted=0, dateRange={"fromDate": "", "toDate": ""})

    total_inserted = 0
    total_updated = 0
    total_matched = 0
    machine_statuses = []
    
    # 2. Iterate machines independently
    for machine in machines:
        serial_number = machine.get("serialNumber")
        # Prevent concurrent jobs from overlapping on the same machine
        if machine.get("syncStatus") == "PROCESSING":
            logger.warning(f"Machine {serial_number} is currently processing. Skipping.")
            machine_statuses.append({
                "serialNumber": serial_number,
                "status": "SKIPPED",
                "error": "Currently processing in another job"
            })
            continue
            
        result = await sync_essl_machine(db, machine, fallback_from_date=from_date, fallback_to_date=to_date)
        if result.get("status") == "SUCCESS":
            total_inserted += result.get("rawInserted", 0)
            total_updated += result.get("rawUpdated", 0)
            total_matched += result.get("rawMatched", 0)
            machine_statuses.append({
                "serialNumber": serial_number,
                "status": "SUCCESS"
            })
        else:
            machine_statuses.append({
                "serialNumber": serial_number,
                "status": "FAILED",
                "error": result.get("error", "Unknown error")
            })

    now = datetime.now(timezone.utc)
    return SyncResponse(
        rawInserted=total_inserted,
        rawUpdated=total_updated,
        rawMatched=total_matched,
        attendanceUpserted=0,
        dateRange={
            "fromDate": (from_date or now).isoformat(),
            "toDate": (to_date or now).isoformat(),
        },
        machines=machine_statuses
    )


async def sync_user(db, emp_id: str, from_date: Optional[datetime] = None, to_date: Optional[datetime] = None) -> dict:
    """Fetch and sync attendance for a single employee across all active machines."""
    logger = logging.getLogger("sync_service")
    
    cursor = db.essl_machines.find({"status": "Active"})
    machines = await cursor.to_list(length=None)
    
    if not machines:
        logger.warning("No active ESSL machines found for user sync.")
        return {"empId": emp_id, "status": "FAILED", "error": "No active machines configured"}

    await db.users.update_one({"empId": emp_id}, {"$set": {"dataSyncStatus": "processing"}})

    total_inserted = 0
    total_matched = 0
    parsed_total_data = []
    
    try:
        from pymongo.errors import DuplicateKeyError
        from .attendance_service import build_raw_log_document
        sync_batch_id = str(uuid4())
        
        for machine in machines:
            serial_number = machine.get("serialNumber")
            machine_id = str(machine["_id"])
            
            if not serial_number:
                continue
                
            try:
                client = build_essl_client(serial_number)
                records = await _fetch_transactions(client, from_date=from_date, to_date=to_date)
                
                parsed_data = [r for r in records if r.get("empId") == emp_id]
                for p in parsed_data:
                    p["machineId"] = machine_id
                    p["serialNumber"] = serial_number
                    
                parsed_total_data.extend(parsed_data)
            except Exception as e:
                logger.error(f"User sync failed on machine {serial_number} for {emp_id}: {e}")
                continue

        from .attendance_service import upsert_raw_logs
        raw_result = await upsert_raw_logs(db, parsed_total_data, sync_batch_id)
        total_inserted = raw_result.get("inserted", 0)
        total_matched = raw_result.get("matched_existing", 0)

        # Push to Dirty Queue
        dirty_queue = DirtyQueueService(db)
        fd_iso = from_date.isoformat() if from_date else datetime.now(timezone.utc).isoformat()
        td_iso = to_date.isoformat() if to_date else datetime.now(timezone.utc).isoformat()
        
        emp_record = await db.employees.find_one({"employeeCode": emp_id})
        emp_uuid = emp_record["employeeId"] if emp_record else emp_id
        
        await dirty_queue.push(
            employee_id=emp_uuid,
            employee_code=emp_id,
            from_date=fd_iso,
            to_date=td_iso,
            reason="eSSL Multi-Machine Sync User logs received",
            trigger="ESSL_SYNC"
        )
        
        raw_user = await db.users.find_one({"empId": emp_id})
        user = DictAttrWrapper(raw_user)
        user.lastSyncAt = datetime.now(timezone.utc)
        await db.users.update_one({"empId": emp_id}, {"$set": {"dataSyncStatus": "completed", "lastSyncAt": user.lastSyncAt}})

        return {
            "empId": emp_id,
            "rawInserted": total_inserted,
            "rawUpdated": 0,
            "rawMatched": total_matched,
            "attendanceUpserted": 0,
            "lastSyncAt": user.lastSyncAt,
        }
    except Exception as exc:
        await db.users.update_one({"empId": emp_id}, {"$set": {"dataSyncStatus": "failed"}})
        logger.exception("Sync failed for empId %s", emp_id)
        raise


async def sync_user_incremental(db, emp_id: str) -> dict:
    raw_user = await db.users.find_one({"empId": emp_id})
    user = DictAttrWrapper(raw_user)

    now = datetime.now(timezone.utc)
    if not user.lastSyncAt or user.lastSyncAt > now:
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
            continue
    return results
