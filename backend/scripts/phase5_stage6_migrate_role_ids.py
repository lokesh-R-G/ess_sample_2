import argparse
from pymongo import MongoClient

# Ensure backend root is on sys.path for internal imports
import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from app.core.config import get_settings

CANONICAL_ROLE_MAP = {
    "ROLE_EMPLOYEE": "employee",
    "ROLE_MANAGER": "manager",
    "ROLE_HR": "hr",
    "ROLE_ADMIN": "admin",
    "ROLE_ACCOUNTS": "accounts",
    "ROLE_ACCOUNTS_MD": "accounts_md",
    "ROLE_SUPER_ADMIN": "super_admin",
}

def main(dry_run: bool = True):
    settings = get_settings()
    client = MongoClient(settings.mongo_uri.strip())
    db = client[settings.mongo_db_name.strip()]

    users_coll = db["users"]
    
    plan = []
    for user in users_coll.find({}):
        role_id = user.get("roleId")
        if role_id in CANONICAL_ROLE_MAP:
            new_role_id = CANONICAL_ROLE_MAP[role_id]
            plan.append({
                "userId": str(user.get("_id")),
                "empId": user.get("empId"),
                "currentRoleId": role_id,
                "newRoleId": new_role_id
            })

    if not plan:
        print("No users require roleId canonicalization.")
        return

    print(f"Plan to update {len(plan)} users to canonical roleIds:")
    for p in plan:
        print(f"  User {p['empId']} ({p['userId']}): {p['currentRoleId']} -> {p['newRoleId']}")

    if dry_run:
        print("\nDRY RUN completed. Run with --execute to apply changes.")
        return

    updated_count = 0
    for p in plan:
        res = users_coll.update_one(
            {"_id": p["userId"] if not isinstance(p["userId"], str) else p["userId"]},
            {"$set": {"roleId": p["newRoleId"]}}
        )
        if res.matched_count == 0:
            # Fallback for ObjectId
            from bson import ObjectId
            res = users_coll.update_one(
                {"_id": ObjectId(p["userId"])},
                {"$set": {"roleId": p["newRoleId"]}}
            )
        updated_count += res.modified_count

    print(f"\nExecution completed. Successfully updated {updated_count} users.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Canonical RoleId Migration")
    parser.add_argument("--execute", action="store_true", help="Apply updates to DB")
    args = parser.parse_args()
    
    main(dry_run=not args.execute)
