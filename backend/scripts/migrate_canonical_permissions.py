import json, datetime, os, sys
from pymongo import MongoClient
# Ensure repository root is in PYTHONPATH for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.core.config import get_settings

def main():
    # Load settings and connect to DB
    settings = get_settings()
    client = MongoClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]

    # ---------- STEP 1: BACKUP ----------
    permissions = list(db.permissions.find())
    role_perms = list(db.role_permissions.find())
    # Artifact directory (conversation specific)
    conv_id = "6ed04bf3-0d2b-4c5c-9063-59d073c4f9d0"
    backup_dir = os.path.join(
        r"C:/Users/dell/.gemini/antigravity-ide/brain", conv_id
    )
    os.makedirs(backup_dir, exist_ok=True)
    perm_backup_path = os.path.join(backup_dir, "permissions_backup.json")
    rp_backup_path = os.path.join(backup_dir, "role_permissions_backup.json")
    with open(perm_backup_path, "w", encoding="utf-8") as f:
        json.dump(permissions, f, default=str, indent=2)
    with open(rp_backup_path, "w", encoding="utf-8") as f:
        json.dump(role_perms, f, default=str, indent=2)

    # ---------- STEP 2 & 3: RECONCILE & CREATE ----------
    canonical = [
        "employee.read", "employee.manage",
        "attendance.read", "attendance.manage", "attendance.sync",
        "leave.read", "leave.apply", "leave.manage", "leave.approve",
        "reimbursement.read", "reimbursement.create", "reimbursement.manage", "reimbursement.approve",
        "payroll.read", "payroll.salary.read", "payroll.pf.read", "payroll.esi.read",
        "payroll.branch_summary.read", "payroll.calculate", "payroll.publish",
        "payroll.cycle.read", "payroll.cycle.manage",
        "organization.read", "organization.manage",
        "policy.attendance.manage", "policy.leave.manage", "policy.reimbursement.manage",
        "policy.weekly_off.manage", "policy.shift.manage",
        "workflow.read", "workflow.manage", "workflow.approve",
        "essl.sync", "essl.recovery_sync",
    ]

    migrated_existing = 0
    created_new = 0
    conflicts = []
    existing_permission_ids = set()

    # Process existing permission documents
    for doc in permissions:
        perm_code = doc.get("permissionCode")
        perm_id = doc.get("permissionId")
        if perm_code in canonical:
            if perm_id and perm_id != perm_code:
                conflicts.append(str(doc.get("_id")))
                continue
            update_fields = {"permissionId": perm_code}
            if not doc.get("name"):
                update_fields["name"] = perm_code
            if not doc.get("module"):
                update_fields["module"] = perm_code.split(".")[0]
            if not doc.get("action"):
                update_fields["action"] = perm_code.split(".")[1] if "." in perm_code else ""
            if "isActive" not in doc:
                update_fields["isActive"] = True
            if "version" not in doc:
                update_fields["version"] = 1
            if "createdAt" not in doc:
                now = datetime.datetime.utcnow()
                update_fields["createdAt"] = now
                update_fields["updatedAt"] = now
            db.permissions.update_one({"_id": doc["_id"]}, {"$set": update_fields})
            migrated_existing += 1
            existing_permission_ids.add(perm_code)
        else:
            if perm_id:
                if perm_id in existing_permission_ids:
                    conflicts.append(str(doc.get("_id")))
                else:
                    existing_permission_ids.add(perm_id)

    # Insert missing canonical permissions
    for pid in canonical:
        if pid not in existing_permission_ids:
            now = datetime.datetime.utcnow()
            new_doc = {
                "permissionId": pid,
                "name": pid,
                "description": "",
                "module": pid.split(".")[0],
                "action": pid.split(".")[1] if "." in pid else "",
                "isActive": True,
                "createdAt": now,
                "updatedAt": now,
                "version": 1,
            }
            db.permissions.insert_one(new_doc)
            created_new += 1
            existing_permission_ids.add(pid)

    # ---------- STEP 6: Update role_permissions ----------
    updated_rp = 0
    for rp in db.role_permissions.find():
        pcode = rp.get("permissionCode")
        if pcode and pcode in canonical:
            if rp.get("permissionId") != pcode:
                db.role_permissions.update_one({"_id": rp["_id"]}, {"$set": {"permissionId": pcode}})
                updated_rp += 1

    # ---------- STEP 5: Create unique index on permissionId ----------
    try:
        db.permissions.create_index("permissionId", unique=True)
    except Exception as e:
        print(f"Index creation skipped/failed: {e}")

    # Summary output
    summary = {
        "backup_permission_path": perm_backup_path,
        "backup_role_permission_path": rp_backup_path,
        "stats": {
            "existing_permissions_before": len(permissions),
            "existing_permissions_after": db.permissions.count_documents({}),
            "migrated_existing": migrated_existing,
            "created_new": created_new,
            "conflicts_permission_docs": conflicts,
            "updated_role_permissions": updated_rp,
        },
    }
    print(json.dumps(summary, default=str))

if __name__ == "__main__":
    main()
