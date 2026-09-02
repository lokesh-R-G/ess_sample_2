import asyncio
import os
import sys
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

# Load env safely
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME", "essl_production")

async def migrate(dry_run=True):
    print(f"--- STARTING MIGRATION ---")
    print(f"Dry Run: {dry_run}")
    
    if not MONGODB_URI:
        print("Error: MONGODB_URI missing")
        return
        
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    # 1. Attendance Policies
    policies = await db.attendance_policies.find({}).to_list(None)
    for p in policies:
        updates = {}
        if not p.get("attendancePolicyCode"):
            code = "TESTPOLICY001" if "test" in p.get("name", "").lower() else f"POLICY_{str(p['_id'])[-6:].upper()}"
            updates["attendancePolicyCode"] = code
        
        if p.get("version") is None:
            updates["version"] = 1
        if p.get("isCurrent") is None:
            updates["isCurrent"] = True
        if p.get("effectiveFrom") is None:
            updates["effectiveFrom"] = p.get("createdAt", datetime.now(timezone.utc))
            
        if updates:
            print(f"[attendance_policies] {_id(p)} | Updates: {updates}")
            if not dry_run:
                await db.attendance_policies.update_one({"_id": p["_id"]}, {"$set": updates})

    # 2. Weekly Off Policies
    wops = await db.weekly_off_policies.find({}).to_list(None)
    for w in wops:
        updates = {}
        if not w.get("weeklyOffPolicyCode"):
            code = f"WOP_{str(w['_id'])[-6:].upper()}"
            updates["weeklyOffPolicyCode"] = code
        
        if w.get("version") is None:
            updates["version"] = 1
        if w.get("isCurrent") is None:
            updates["isCurrent"] = True
        if w.get("effectiveFrom") is None:
            updates["effectiveFrom"] = w.get("createdAt", datetime.now(timezone.utc))
            
        if updates:
            print(f"[weekly_off_policies] {_id(w)} | Updates: {updates}")
            if not dry_run:
                await db.weekly_off_policies.update_one({"_id": w["_id"]}, {"$set": updates})

    # 3. Holiday Calendars
    cals = await db.holiday_calendars.find({}).to_list(None)
    for c in cals:
        updates = {}
        if not c.get("holidayCalendarCode"):
            code = f"HCAL_{str(c['_id'])[-6:].upper()}"
            updates["holidayCalendarCode"] = code
        
        if c.get("version") is None:
            updates["version"] = 1
        if c.get("isCurrent") is None:
            updates["isCurrent"] = True
            
        if updates:
            print(f"[holiday_calendars] {_id(c)} | Updates: {updates}")
            if not dry_run:
                await db.holiday_calendars.update_one({"_id": c["_id"]}, {"$set": updates})
                
    # 4. Holidays
    hols = await db.holiday_dates.find({}).to_list(None)
    for h in hols:
        updates = {}
        if not h.get("holidayCode"):
            code = f"HOL_{str(h['_id'])[-6:].upper()}"
            updates["holidayCode"] = code
        
        if h.get("version") is None:
            updates["version"] = 1
        if h.get("isCurrent") is None:
            updates["isCurrent"] = True
            
        if updates:
            print(f"[holiday_dates] {_id(h)} | Updates: {updates}")
            if not dry_run:
                await db.holiday_dates.update_one({"_id": h["_id"]}, {"$set": updates})
                
    # 5. Shifts (already have shiftCode but need to ensure version/isCurrent/effectiveFrom)
    shifts = await db.shifts.find({}).to_list(None)
    for s in shifts:
        updates = {}
        if s.get("version") is None:
            updates["version"] = 1
        if s.get("isCurrent") is None:
            updates["isCurrent"] = True
        if s.get("effectiveFrom") is None:
            updates["effectiveFrom"] = s.get("createdAt", datetime.now(timezone.utc))
            
        if updates:
            print(f"[shifts] {_id(s)} | Updates: {updates}")
            if not dry_run:
                await db.shifts.update_one({"_id": s["_id"]}, {"$set": updates})

    print("--- MIGRATION COMPLETE ---")

def _id(doc):
    return str(doc["_id"])

if __name__ == "__main__":
    import sys
    dry_run = "--execute" not in sys.argv
    asyncio.run(migrate(dry_run=dry_run))
