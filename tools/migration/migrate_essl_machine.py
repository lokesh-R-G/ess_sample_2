import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))
from app.db.mongo import get_database

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

async def migrate_essl_machine():
    db = get_database()
    
    # Check if a machine already exists
    existing = await db.essl_machines.find_one({})
    if existing:
        print("✅ essl_machines collection already populated. Migration skipped.")
        return

    # Extract legacy serial number
    serial_number = os.getenv("ESSL_SERIAL_NUMBER", "").strip()
    if not serial_number:
        print("⚠️ No ESSL_SERIAL_NUMBER found in .env. Nothing to migrate.")
        return

    # Create the new document
    now = datetime.now(timezone.utc)
    machine_id = str(uuid.uuid4())
    
    doc = {
        "machineId": machine_id,
        "serialNumber": serial_number,
        "machineName": "Primary ESSL Device (Migrated)",
        "companyId": None,
        "branchId": None,
        "isActive": True,
        "syncStatus": "IDLE",
        "createdAt": now,
        "updatedAt": now
    }
    
    await db.essl_machines.insert_one(doc)
    print(f"🎉 Successfully migrated legacy serial number '{serial_number}' to essl_machines collection!")
    print("   You may now safely remove ESSL_SERIAL_NUMBER from your .env file.")

if __name__ == "__main__":
    asyncio.run(migrate_essl_machine())
