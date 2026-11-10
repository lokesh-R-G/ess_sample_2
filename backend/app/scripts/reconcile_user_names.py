#!/usr/bin/env python3
"""
Reconciliation & Migration Script: Populate missing employee names in the `users` collection.
Supports:
  --dry-run: Preview updates without writing to database
  --apply: Apply updates to users collection
  --employee-id <id>: Target a specific employeeId or employeeCode
  --limit <n>: Limit number of records to process
"""

import sys
import os
import argparse
import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from dotenv import load_dotenv

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env')))
from app.services.user_sync_service import get_authoritative_employee_name

async def run_reconciliation(args):
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    if not mongo_uri or not db_name:
        print("[ERROR] MONGODB_URI or MONGODB_DB_NAME not set in environment.")
        sys.exit(1)

    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]

    print("=" * 60)
    print("USER NAME RECONCILIATION & MIGRATION")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    if args.employee_id:
        print(f"Target Employee Filter: {args.employee_id}")
    if args.limit:
        print(f"Limit: {args.limit}")
    print("=" * 60)

    # 1. Query users
    query = {}
    if args.employee_id:
        query["$or"] = [
            {"employeeId": str(args.employee_id)},
            {"employeeCode": str(args.employee_id)},
            {"empId": str(args.employee_id)},
            {"username": str(args.employee_id)}
        ]

    users_cursor = db.users.find(query)
    users = await users_cursor.to_list(length=None)

    total_scanned = len(users)
    already_valid = []
    to_update = []
    unmatched = []
    ambiguous = []

    for u in users:
        user_id = str(u.get("_id"))
        existing_name = (u.get("name") or "").strip()
        emp_id = u.get("empId")
        employee_id = u.get("employeeId")
        employee_code = u.get("employeeCode") or emp_id

        # Safety Check: Do not modify users who already have valid names
        if existing_name:
            already_valid.append({
                "userId": user_id,
                "empId": emp_id,
                "name": existing_name
            })
            continue

        # Check for ambiguity: multiple employees matching
        candidates = []
        if employee_id:
            c1 = await db.employees.find({"employeeId": str(employee_id)}).to_list(10)
            candidates.extend(c1)
        if employee_code:
            c2 = await db.employees.find({"employeeCode": str(employee_code)}).to_list(10)
            for c in c2:
                if str(c["_id"]) not in [str(x["_id"]) for x in candidates]:
                    candidates.append(c)

        if len(candidates) > 1:
            ambiguous.append({
                "userId": user_id,
                "empId": emp_id,
                "employeeId": employee_id,
                "reason": f"Multiple employee candidates found ({len(candidates)})"
            })
            continue

        # Resolve authoritative name
        resolved_name, emp_doc = await get_authoritative_employee_name(
            db,
            employee_id=employee_id,
            employee_code=employee_code
        )

        if not resolved_name:
            unmatched.append({
                "userId": user_id,
                "empId": emp_id,
                "employeeId": employee_id,
                "reason": "No employee or personal profile with valid name found"
            })
            continue

        resolved_emp_id = emp_doc.get("employeeId") if emp_doc else employee_id

        to_update.append({
            "_id": u["_id"],
            "userId": user_id,
            "empId": emp_id,
            "resolvedEmployeeId": resolved_emp_id,
            "currentName": existing_name,
            "proposedName": resolved_name
        })

    # Apply limit if specified
    if args.limit and args.limit > 0:
        to_update = to_update[:args.limit]

    print(f"\nExecution Summary:")
    print(f"  Total Users Scanned:     {total_scanned}")
    print(f"  Already Valid Names:     {len(already_valid)}")
    print(f"  Eligible for Update:     {len(to_update)}")
    print(f"  Unmatched Records:       {len(unmatched)}")
    print(f"  Ambiguous Records:       {len(ambiguous)}")

    if to_update:
        print("\nProposed Updates:")
        for item in to_update:
            print(f"  [User {item['userId']} | empId: {item['empId']}] -> Name: '{item['proposedName']}' (empId: {item['resolvedEmployeeId']})")

    if unmatched:
        print("\nUnmatched Users (No Name Found):")
        for item in unmatched:
            print(f"  [User {item['userId']} | empId: {item['empId']} | employeeId: {item['employeeId']}] - {item['reason']}")

    if ambiguous:
        print("\nAmbiguous Users (Skipped for safety):")
        for item in ambiguous:
            print(f"  [User {item['userId']} | empId: {item['empId']}] - {item['reason']}")

    # Apply updates if requested
    if args.apply:
        if not to_update:
            print("\nNo records to update.")
        else:
            print(f"\nApplying {len(to_update)} updates to database...")
            now = datetime.now(timezone.utc)
            applied_count = 0
            for item in to_update:
                update_fields = {
                    "name": item["proposedName"],
                    "updatedAt": now
                }
                if item["resolvedEmployeeId"]:
                    update_fields["employeeId"] = str(item["resolvedEmployeeId"])

                res = await db.users.update_one(
                    {"_id": item["_id"]},
                    {"$set": update_fields}
                )
                if res.modified_count > 0:
                    applied_count += 1
            print(f"Successfully updated {applied_count} user records.")
    else:
        print("\n[DRY RUN] No changes were written to the database. Use --apply to execute.")

def main():
    parser = argparse.ArgumentParser(description="Populate missing employee names in users collection.")
    parser.add_argument("--dry-run", action="store_true", help="Preview proposed updates without modifying data")
    parser.add_argument("--apply", action="store_true", help="Execute the updates against database")
    parser.add_argument("--employee-id", type=str, default=None, help="Process only a specific employeeId or employeeCode")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records to process")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Please specify either --dry-run or --apply.")
        parser.print_help()
        sys.exit(1)

    asyncio.run(run_reconciliation(args))

if __name__ == "__main__":
    main()
