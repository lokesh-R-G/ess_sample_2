import asyncio
import logging
import sys
from datetime import datetime, timezone
import argparse

sys.path.append(".")
from app.db.mongo import get_database
from app.services.attendance_service import create_fingerprint

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("migrate_fingerprints")

async def migrate_essl_fingerprints():
    db = get_database()

    logger.info("Starting ESSL Fingerprint Migration...")

    # 1. Drop incorrect unique index
    try:
        await db.attendance_logs.drop_index("empId_1_timestamp_1")
        logger.info("Successfully dropped incorrect empId_1_timestamp_1 index")
    except Exception as e:
        logger.info(f"empId_1_timestamp_1 index not found or already dropped: {e}")

    # 2. Resolve the single canonical machine (assuming a pre-multi-machine state with exactly 1 active machine)
    cursor = db.essl_machines.find({"status": "Active"})
    machines = await cursor.to_list(length=None)
    
    if len(machines) == 0:
        logger.error("No active ESSL machines found to attribute legacy records to.")
        return
    elif len(machines) > 1:
        logger.warning(f"Multiple active ESSL machines found ({len(machines)}). Cannot deterministically assign provenance for orphaned records without explicit instruction.")
        return

    canonical_machine = machines[0]
    machine_id = str(canonical_machine["_id"])
    serial_number = canonical_machine.get("serialNumber")

    if not serial_number:
        logger.error(f"Canonical machine {machine_id} has no serial number.")
        return

    logger.info(f"Canonical machine resolved: {serial_number} ({machine_id})")

    # 3. Find legacy records missing provenance
    query = {
        "source": "essl",
        "$or": [
            {"serialNumber": {"$exists": False}},
            {"serialNumber": None},
            {"serialNumber": ""}
        ]
    }
    
    total_legacy = await db.attendance_logs.count_documents(query)
    logger.info(f"Found {total_legacy} legacy records requiring migration.")

    if total_legacy == 0:
        logger.info("No records require migration.")
        return

    migrated_count = 0
    collision_count = 0
    
    cursor = db.attendance_logs.find(query)
    async for record in cursor:
        record_id = record["_id"]
        emp_id = record.get("empId")
        timestamp = record.get("timestamp")
        raw_payload = record.get("rawPayload")

        if not all([emp_id, timestamp, raw_payload]):
            logger.warning(f"Record {record_id} is malformed. Skipping.")
            continue

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        new_fingerprint = create_fingerprint(
            emp_id=emp_id,
            timestamp=timestamp,
            raw_payload=raw_payload,
            serial_number=serial_number
        )

        try:
            await db.attendance_logs.update_one(
                {"_id": record_id},
                {
                    "$set": {
                        "fingerprint": new_fingerprint,
                        "serialNumber": serial_number,
                        "machineId": machine_id,
                        "updatedAt": datetime.now(timezone.utc)
                    }
                }
            )
            migrated_count += 1
            if migrated_count % 100 == 0:
                logger.info(f"Migrated {migrated_count}/{total_legacy} records...")
        except Exception as e:
            if "DuplicateKeyError" in str(type(e)):
                logger.warning(f"Collision for record {record_id} with fingerprint {new_fingerprint}. Already exists.")
                collision_count += 1
                # If there's a collision, it means this exact punch was already re-synced under the new format.
                # The legacy record without provenance is redundant.
            else:
                logger.error(f"Failed to migrate record {record_id}: {e}")

    logger.info(f"Migration complete. Migrated: {migrated_count}, Collisions (redundant): {collision_count}")


if __name__ == "__main__":
    asyncio.run(migrate_essl_fingerprints())
