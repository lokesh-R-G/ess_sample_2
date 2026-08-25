import argparse
import json
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

# Ensure backend root is on sys.path for internal imports
import os, sys
project_root = os.path.abspath('C:/ess/ess_sample_2/backend')
sys.path.append(project_root)

from app.core.config import get_settings

# Canonical role mapping from legacy role name to roleId
CANONICAL_ROLE_MAP = {
    "Employee": "employee",
    "Manager": "manager",
    "HR": "hr",
    "Admin": "admin",
    "Accounts": "accounts",
    "Accounts MD": "accounts_md",
    "Super Admin": "super_admin",
    "ROLE_EMPLOYEE": "employee",
    "ROLE_MANAGER": "manager",
    "ROLE_HR": "hr",
    "ROLE_ADMIN": "admin",
    "ROLE_ACCOUNTS": "accounts",
    "ROLE_ACCOUNTS_MD": "accounts_md",
    "ROLE_SUPER_ADMIN": "super_admin",
}

def resolve_user(user, employees_coll, emp_hist_coll, companies_coll, branchs_coll, roles_coll):
    """Resolve a user to its canonical role and verify company/branch.
    Returns a dict with resolution data or a skip flag.
    """
    emp_id = user.get("empId")
    legacy_role = user.get("role")
    target_role_id = CANONICAL_ROLE_MAP.get(legacy_role)

    # Resolve employee via employeeCode (skip bootstrap and test fixtures earlier)
    employee = employees_coll.find_one({"employeeCode": emp_id})
    if not employee:
        return {"skip": True, "reason": "EMPLOYEE_NOT_FOUND"}
    canonical_employee_id = employee.get("employeeId") or employee.get("_id")

    # Current employment history (isCurrent=True)
    hist = emp_hist_coll.find_one({"employeeId": canonical_employee_id, "isCurrent": True})
    if not hist:
        return {"skip": True, "reason": "EMPLOYMENT_HISTORY_NOT_FOUND"}

    # Helper to fetch by ObjectId or string
    def fetch_by_id(coll, id_val):
        if not id_val:
            return None, None
        try:
            oid = ObjectId(str(id_val))
            doc = coll.find_one({"_id": oid})
            if doc:
                return doc, "ObjectId"
        except Exception:
            pass
        doc = coll.find_one({"_id": str(id_val)})
        if doc:
            return doc, "String"
        return None, None

    company_doc, company_id_type = fetch_by_id(companies_coll, hist.get("companyId"))
    branch_doc, branch_id_type = fetch_by_id(branchs_coll, hist.get("branchId"))
    branch_company_match = None
    if company_doc and branch_doc:
        branch_company_match = branch_doc.get("companyId") == hist.get("companyId")
    return {
        "skip": False,
        "canonical_role_id": target_role_id,
        "current_role_id": user.get("roleId"),
        "company_doc": company_doc,
        "branch_doc": branch_doc,
        "branch_company_match": branch_company_match,
        "company_id_type": company_id_type,
        "branch_id_type": branch_id_type,
    }

def main(dry_run: bool = True):
    settings = get_settings()
    client = MongoClient(settings.mongo_uri.strip())
    db = client[settings.mongo_db_name.strip()]

    users_coll = db["users"]
    employees_coll = db["employees"]
    emp_hist_coll = db["employee_employment_histories"]
    companies_coll = db["companies"]
    branchs_coll = db["branchs"]
    roles_coll = db["roles"]
    log_coll = db["phase4_user_migration_log"]

    plan = []
    for user in users_coll.find({}):
        emp_id = user.get("empId")
        # Skip bootstrap and test fixtures
        if emp_id == "0001" or (isinstance(emp_id, str) and emp_id.startswith("TEST-")):
            plan.append({
                "userId": str(user.get("_id")),
                "empId": emp_id,
                "action": "skip",
                "reason": "bootstrap_or_test_fixture",
            })
            continue
        resolution = resolve_user(user, employees_coll, emp_hist_coll, companies_coll, branchs_coll, roles_coll)
        if resolution.get("skip"):
            plan.append({
                "userId": str(user.get("_id")),
                "empId": emp_id,
                "action": "skip",
                "reason": resolution.get("reason"),
            })
            continue
        target_role_id = resolution.get("canonical_role_id")
        current_role_id = user.get("roleId")
        current_auth_version = user.get("authorizationVersion")
        changes = {}
        if current_role_id != target_role_id:
            changes["roleId"] = {"from": current_role_id, "to": target_role_id}
        if current_auth_version != 1:
            changes["authorizationVersion"] = {"from": current_auth_version, "to": 1}
        if changes:
            plan.append({
                "userId": str(user.get("_id")),
                "empId": emp_id,
                "action": "update",
                "changes": changes,
                "current_role_id": current_role_id,
                "target_role_id": target_role_id,
                "current_auth_version": current_auth_version,
                "target_auth_version": 1,
            })
        else:
            plan.append({
                "userId": str(user.get("_id")),
                "empId": emp_id,
                "action": "no_change",
            })

    updates = [p for p in plan if p["action"] == "update"]
    skips = [p for p in plan if p["action"] == "skip"]
    no_change = [p for p in plan if p["action"] == "no_change"]

    print("--- Phase 4 Migration Dry-Run Summary ---")
    print(f"Total users examined: {len(plan)}")
    print(f"Will be migrated (updates): {len(updates)}")
    print(f"Will be skipped (bootstrap / test fixtures): {len(skips)}")
    print(f"No changes needed: {len(no_change)}")
    print("\nDetails of users to be migrated:")
    for u in updates:
        print(f"- userId: {u['userId']} (empId={u['empId']})")
        for fld, vals in u["changes"].items():
            print(f"    {fld}: {vals['from']} -> {vals['to']}")
    print("\nDry-run complete. No database writes were performed.")

    if not dry_run:
        for u in updates:
            user_id = ObjectId(u["userId"]) if ObjectId.is_valid(u["userId"]) else u["userId"]
            update_doc = {}
            if "roleId" in u["changes"]:
                update_doc["roleId"] = u["target_role_id"]
            if "authorizationVersion" in u["changes"]:
                update_doc["authorizationVersion"] = 1
            if update_doc:
                users_coll.update_one({"_id": user_id}, {"$set": update_doc})
                # Idempotent log creation
                existing = log_coll.find_one({"userId": user_id, "changedBy": "phase4_user_migration"})
                if not existing:
                    log_coll.insert_one({
                        "userId": user_id,
                        "prevRoleId": u["current_role_id"],
                        "newRoleId": u["target_role_id"],
                        "prevAuthVersion": u["current_auth_version"],
                        "newAuthVersion": 1,
                        "changedBy": "phase4_user_migration",
                        "changedAt": datetime.utcnow(),
                    })
        print(f"Migration applied to {len(updates)} users. Logs created where needed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 4 user migration (dry‑run by default)")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry‑run mode (default)")
    parser.add_argument("--execute", action="store_true", help="Execute the migration (writes to DB)")
    args = parser.parse_args()
    # Dry‑run unless --execute is supplied
    main(dry_run=not args.execute)
