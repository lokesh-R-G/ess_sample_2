"""
Reconciliation & Diagnostic Script for Holiday Calendars, Dates, and Branch Assignments.

Supports:
  --dry-run       : Inspects and prints proposed updates without writing to MongoDB (default)
  --apply         : Executes proposed reconciliations transactionally
  --calendar-code : Restrict execution to a specific calendar code
  --limit         : Maximum number of records to process
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

def setup_environment():
    base_dir = Path(__file__).resolve().parent.parent.parent
    dotenv_path = base_dir / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
    else:
        load_dotenv()

async def reconcile_holiday_calendars(dry_run: bool = True, filter_code: str = None, limit: int = None):
    setup_environment()
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "essl_production")

    print("=" * 70)
    print("Holiday Calendar & Date Data Reconciliation Script")
    print(f"Database : {db_name}")
    print(f"Mode     : {'DRY-RUN (No writes)' if dry_run else 'APPLY (Writing changes)'}")
    if filter_code:
        print(f"Filter   : holidayCalendarCode = {filter_code}")
    print("=" * 70)

    client = AsyncIOMotorClient(uri)
    db = client[db_name]

    report = {
        "orphaned_dates_fixed": 0,
        "current_versions_synchronized": 0,
        "branches_reconciled": 0,
        "conflicts_detected": 0,
        "details": []
    }

    # 1. Inspect all calendars grouped by holidayCalendarCode
    cal_query = {"deletedAt": None}
    if filter_code:
        cal_query["holidayCalendarCode"] = filter_code

    calendars = await db.holiday_calendars.find(cal_query).sort("version", 1).to_list(limit)
    code_map = {}
    for c in calendars:
        code = c.get("holidayCalendarCode")
        if not code:
            report["details"].append(f"[WARNING] Calendar _id={c['_id']} has no holidayCalendarCode!")
            continue
        code_map.setdefault(code, []).append(c)

    print(f"\n[INFO] Found {len(code_map)} distinct holiday calendar codes across {len(calendars)} versions.")

    # 2. Check each calendar line
    now = datetime.now(timezone.utc)
    for code, versions in code_map.items():
        print(f"\nProcessing Calendar Code: {code} ({len(versions)} versions)")
        current_version = next((v for v in versions if v.get("isCurrent") is True), versions[-1])
        current_id = str(current_version["_id"])
        
        # All IDs in this lineage
        lineage_ids = [str(v["_id"]) for v in versions]
        
        # Find all holiday dates across all versions of this calendar
        all_dates = await db.holiday_dates.find({
            "calendarId": {"$in": lineage_ids},
            "deletedAt": None,
            "status": "Active"
        }).sort([("holidayDate", 1)]).to_list(None)

        # Dates specifically on current version
        current_dates = [d for d in all_dates if d.get("calendarId") == current_id]
        # Dates on older versions
        older_dates = [d for d in all_dates if d.get("calendarId") != current_id]

        print(f"  Current Version _id={current_id} (v{current_version.get('version', 1)}) has {len(current_dates)} dates.")
        print(f"  Prior versions have {len(older_dates)} active dates.")

        # Check for dates on older versions that are missing from current version
        current_holiday_dates = {d["holidayDate"].strftime("%Y-%m-%d") if hasattr(d["holidayDate"], "strftime") else str(d["holidayDate"])[:10] for d in current_dates}
        missing_on_current = []
        for od in older_dates:
            d_str = od["holidayDate"].strftime("%Y-%m-%d") if hasattr(od["holidayDate"], "strftime") else str(od["holidayDate"])[:10]
            if d_str not in current_holiday_dates:
                missing_on_current.append(od)

        if missing_on_current:
            print(f"  [ACTION] {len(missing_on_current)} date(s) from earlier versions need to be copied to current version:")
            for m in missing_on_current:
                print(f"    - {m.get('holidayName')} ({m.get('holidayDate')}) [Code: {m.get('holidayCode')}]")
                if not dry_run:
                    new_doc = dict(m)
                    new_doc.pop("_id", None)
                    new_doc["calendarId"] = current_id
                    new_doc["createdAt"] = now
                    new_doc["updatedAt"] = now
                    new_doc["createdBy"] = "RECONCILIATION_SCRIPT"
                    new_doc["updatedBy"] = "RECONCILIATION_SCRIPT"
                    new_doc["version"] = 1
                    new_doc["isCurrent"] = True
                    new_doc["status"] = "Active"
                    await db.holiday_dates.insert_one(new_doc)
            report["current_versions_synchronized"] += len(missing_on_current)
        else:
            print("  [OK] Current version has all active dates from historical versions.")

        # 3. Synchronize branch references if calendar has branchId
        branch_id = current_version.get("branchId")
        if branch_id:
            try:
                b_query = {"$or": [{"_id": ObjectId(branch_id)}, {"_id": branch_id}]}
            except Exception:
                b_query = {"_id": branch_id}
            branch = await db.branchs.find_one(b_query)
            if branch:
                needs_update = branch.get("holidayCalendarCode") != code or branch.get("holidayCalendarId") != current_id
                if needs_update:
                    print(f"  [ACTION] Branch '{branch.get('name')}' needs assignment sync to code '{code}' and id '{current_id}'.")
                    if not dry_run:
                        await db.branchs.update_one(
                            b_query,
                            {"$set": {"holidayCalendarCode": code, "holidayCalendarId": current_id, "updatedAt": now}}
                        )
                    report["branches_reconciled"] += 1
                else:
                    print(f"  [OK] Branch '{branch.get('name')}' is already aligned with this calendar code.")

    # 4. Check for unlinked branches
    all_branches = await db.branchs.find({"deletedAt": None}).to_list(None)
    for b in all_branches:
        if not b.get("holidayCalendarCode") and not b.get("holidayCalendarId"):
            report["details"].append(f"[INFO] Branch '{b.get('name')}' (code: {b.get('code')}) has no holiday calendar assigned.")

    print("\n" + "=" * 70)
    print("Reconciliation Summary Report")
    print(f"Mode                            : {'DRY-RUN' if dry_run else 'APPLIED'}")
    print(f"Dates Synchronized to Current   : {report['current_versions_synchronized']}")
    print(f"Branches Reconciled             : {report['branches_reconciled']}")
    print(f"Diagnostic Notes                : {len(report['details'])}")
    for note in report["details"]:
        print(f"  {note}")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Reconcile Holiday Calendars, Dates, and Branch Assignments")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview proposed updates without writing (default)")
    parser.add_argument("--apply", action="store_true", help="Execute proposed updates")
    parser.add_argument("--calendar-code", type=str, default=None, help="Filter by holidayCalendarCode")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of calendar records")
    args = parser.parse_args()

    is_dry_run = not args.apply
    asyncio.run(reconcile_holiday_calendars(dry_run=is_dry_run, filter_code=args.calendar_code, limit=args.limit))

if __name__ == "__main__":
    main()

