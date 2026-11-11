import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

load_dotenv("backend/.env")
from motor.motor_asyncio import AsyncIOMotorClient

async def migrate_indexes(dry_run: bool = False):
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME", "ess_payroll")
    if not uri:
        print("[ERROR] MONGODB_URI is not set in environment.")
        return

    client = AsyncIOMotorClient(uri)
    db = client[db_name]

    print(f"=== Inspecting Indexes on employees [{db_name}] (dry_run={dry_run}) ===")
    indexes = await db.employees.index_information()
    print("Current indexes:")
    for name, details in indexes.items():
        print(f"  {name}: {details}")

    # Check for incompatible machineId index
    incompatible_name = None
    for name, details in indexes.items():
        keys = details.get("key", [])
        if keys == [("machineId", 1)] and details.get("unique"):
            incompatible_name = name
            break

    if incompatible_name:
        print(f"\n[FOUND] Incompatible index detected: '{incompatible_name}'")
        if not dry_run:
            print(f"[ACTION] Dropping incompatible unique index '{incompatible_name}'...")
            await db.employees.drop_index(incompatible_name)
            print(f"[SUCCESS] Dropped index '{incompatible_name}'.")
        else:
            print(f"[DRY-RUN] Would drop index '{incompatible_name}'.")
    else:
        print("\n[INFO] No incompatible machineId index found on employees collection.")

    # Ensure employee_identifier_registry unique index
    print("\n[ACTION] Ensuring unique index on employee_identifier_registry...")
    if not dry_run:
        await db.employee_identifier_registry.create_index(
            [("identifier", 1)],
            unique=True,
            name="uniq_registry_identifier"
        )
        print("[SUCCESS] Unique index uniq_registry_identifier ensured.")
    else:
        print("[DRY-RUN] Would create uniq_registry_identifier.")

    # Final inspection
    indexes_after = await db.employees.index_information()
    print("\nUpdated indexes on employees:")
    for name, details in indexes_after.items():
        print(f"  {name}: {details}")

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    asyncio.run(migrate_indexes(dry_run=dry_run))

