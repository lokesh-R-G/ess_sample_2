import asyncio
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

load_dotenv("backend/.env")
from motor.motor_asyncio import AsyncIOMotorClient

async def backfill_registry(dry_run: bool = False):
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME", "ess_payroll")
    if not uri:
        print("[ERROR] MONGODB_URI is not set in environment.")
        return

    client = AsyncIOMotorClient(uri)
    db = client[db_name]

    print(f"=== Starting Identifier Registry Backfill [{db_name}] (dry_run={dry_run}) ===")

    # 1. Ensure unique index on employee_identifier_registry
    try:
        existing = await db.employee_identifier_registry.index_information()
        if not any(
            list(details.get("key", [])) == [("identifier", 1)] and details.get("unique") is True
            for details in existing.values()
        ):
            await db.employee_identifier_registry.create_index(
                [("identifier", 1)],
                unique=True,
            )
        print("[OK] Unique identifier index on employee_identifier_registry is present.")
    except Exception as e:
        print(f"[WARN] Error ensuring index on employee_identifier_registry: {e}")

    # 2. Find all current non-deleted employees
    current_employees = await db.employees.find({
        "deletedAt": None,
        "isCurrent": {"$ne": False}
    }).to_list(1000)

    print(f"Found {len(current_employees)} current, non-deleted employees.")

    # 3. For each employee, assign masterEmployeeId if missing, and record machineId in registry
    registered_count = 0
    now = datetime.now(timezone.utc)

    for emp in current_employees:
        _id = emp["_id"]
        master_id = emp.get("masterEmployeeId")
        if not master_id:
            # Set masterEmployeeId to str(_id)
            master_id = str(_id)
            if not dry_run:
                # Update all historical versions of this employee with this masterEmployeeId
                emp_id_val = emp.get("employeeId")
                if emp_id_val:
                    await db.employees.update_many(
                        {"employeeId": emp_id_val},
                        {"$set": {"masterEmployeeId": master_id}}
                    )
                else:
                    await db.employees.update_one(
                        {"_id": _id},
                        {"$set": {"masterEmployeeId": master_id}}
                    )

        machine_id = emp.get("machineId")
        if machine_id:
            norm_mid = str(machine_id).strip()
            if norm_mid:
                # Check for existing registry document
                existing = await db.employee_identifier_registry.find_one({"identifier": norm_mid})
                if existing:
                    if existing.get("masterEmployeeId") != master_id:
                        print(f"[CONFLICT] Machine ID '{norm_mid}' already registered to another masterEmployeeId: {existing.get('masterEmployeeId')}. Cannot assign to {master_id}. HALTING.")
                        return False
                    else:
                        print(f"[IDEMPOTENT] Machine ID '{norm_mid}' already registered to {master_id}.")
                else:
                    if not dry_run:
                        await db.employee_identifier_registry.insert_one({
                            "identifier": norm_mid,
                            "masterEmployeeId": master_id,
                            "fieldType": "machineId",
                            "createdAt": now,
                            "updatedAt": now
                        })
                    registered_count += 1
                    print(f"[REGISTERED] Machine ID '{norm_mid}' registered for employee {emp.get('employeeCode') or emp.get('employeeId')} (master: {master_id}).")

    print(f"=== Backfill Complete: {registered_count} new machineId registrations created. ===")
    return True

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    asyncio.run(backfill_registry(dry_run=dry_run))

