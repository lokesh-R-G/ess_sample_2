import json, os, sys
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient

# ---------------------------------------------------------------------------
# Load application settings (same mechanism used by the backend).
# ---------------------------------------------------------------------------
# Ensure the backend package is importable.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
try:
    from app.core.config import get_settings
except Exception as e:
    raise RuntimeError(f"Unable to import application settings: {e}")

settings = get_settings()
client = MongoClient(settings.mongo_uri)
db = client[settings.mongo_db_name]

# ---------------------------------------------------------------------------
# Canonical permission catalog – 34 permission identifiers (source of truth).
# ---------------------------------------------------------------------------
canonical_permissions = [
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

# ---------------------------------------------------------------------------
# 1️⃣ Permission collection analysis
# ---------------------------------------------------------------------------
perm_docs = list(db.permissions.find())
perm_total = len(perm_docs)
perm_ids = [doc.get("permissionId") for doc in perm_docs]

# Duplicate permissionIds
seen = set()
duplicate_permission_ids = [pid for pid in perm_ids if pid in seen or seen.add(pid)]

perm_set = set(perm_ids)
canonical_set = set(canonical_permissions)
missing_from_db = sorted(list(canonical_set - perm_set))
unexpected_in_db = sorted(list(perm_set - canonical_set))

# Documents missing required fields
required_fields = {
    "permissionId",
    "name",
    "description",
    "module",
    "action",
    "isActive",
    "createdAt",
    "updatedAt",
    "version",
}
missing_fields_docs = []
unexpected_fields_docs = []
for doc in perm_docs:
    missing = required_fields - doc.keys()
    if missing:
        missing_fields_docs.append({"_id": str(doc.get("_id")), "missing": list(missing)})
    # Any field that is not part of the required set (except _id) is unexpected.
    unexpected = set(doc.keys()) - required_fields - {"_id"}
    if unexpected:
        unexpected_fields_docs.append({"_id": str(doc.get("_id")), "unexpected": list(unexpected)})

# Legacy `permissionCode` field – should equal `permissionId` when present.
legacy_permissioncode_mismatches = []
for doc in perm_docs:
    if "permissionCode" in doc and "permissionId" in doc:
        if doc["permissionCode"] != doc["permissionId"]:
            legacy_permissioncode_mismatches.append({
                "_id": str(doc.get("_id")),
                "permissionCode": doc["permissionCode"],
                "permissionId": doc["permissionId"],
            })

# ---------------------------------------------------------------------------
# 2️⃣ Role‑Permission collection analysis (read‑only)
# ---------------------------------------------------------------------------
rp_docs = list(db.role_permissions.find())
rp_total = len(rp_docs)
role_ids = [doc.get("roleId") for doc in rp_docs]
rp_permission_ids = [doc.get("permissionId") for doc in rp_docs]

null_permission_ids = [str(doc.get("_id")) for doc in rp_docs if not doc.get("permissionId")]
invalid_permission_refs = []
for doc in rp_docs:
    pid = doc.get("permissionId")
    if pid and pid not in perm_set:
        invalid_permission_refs.append({"_id": str(doc.get("_id")), "permissionId": pid})

# Duplicate (roleId, permissionId) combos
combo_seen = set()
duplicate_role_permission_combos = []
for doc in rp_docs:
    combo = (doc.get("roleId"), doc.get("permissionId"))
    if combo in combo_seen:
        duplicate_role_permission_combos.append({"roleId": combo[0], "permissionId": combo[1]})
    else:
        combo_seen.add(combo)

# Legacy `permissionCode` mismatches inside role_permissions
rp_legacy_mismatches = []
for doc in rp_docs:
    if "permissionCode" in doc and "permissionId" in doc:
        if doc["permissionCode"] != doc["permissionId"]:
            rp_legacy_mismatches.append({
                "_id": str(doc.get("_id")),
                "permissionCode": doc["permissionCode"],
                "permissionId": doc["permissionId"],
            })

# ---------------------------------------------------------------------------
# 3️⃣ Index audit – read‑only inspection of actual MongoDB indexes.
# ---------------------------------------------------------------------------
perm_indexes = db.permissions.index_information()
role_indexes = db.roles.index_information()
rp_indexes = db.role_permissions.index_information()

# ---------------------------------------------------------------------------
# 4️⃣ Backup verification – ensure the JSON backups created during Phase 2 exist.
# ---------------------------------------------------------------------------
brain_root = Path(os.getenv("APPDATA", "")) / "gemini" / "antigravity-ide" / "brain" / "6ed04bf3-0d2b-4c5c-9063-59d073c4f9d0"
perm_backup_path = brain_root / "permissions_backup.json"
rp_backup_path = brain_root / "role_permissions_backup.json"
backup_report = {}
for name, path in [("permissions", perm_backup_path), ("role_permissions", rp_backup_path)]:
    if path.is_file():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                backup_report[name] = {"exists": True, "record_count": len(data)}
        except Exception as exc:
            backup_report[name] = {"exists": True, "error": str(exc)}
    else:
        backup_report[name] = {"exists": False}

# ---------------------------------------------------------------------------
# Assemble final report – printed as JSON for easy consumption by the user.
# ---------------------------------------------------------------------------
final_report = {
    "permissions": {
        "total_documents": perm_total,
        "permissionIds": perm_ids,
        "duplicate_permissionIds": duplicate_permission_ids,
        "missing_from_canonical": missing_from_db,
        "unexpected_in_db": unexpected_in_db,
        "documents_missing_required_fields": missing_fields_docs,
        "documents_with_unexpected_fields": unexpected_fields_docs,
        "legacy_permissionCode_mismatches": legacy_permissioncode_mismatches,
    },
    "role_permissions": {
        "total_documents": rp_total,
        "roleIds": role_ids,
        "permissionIds": rp_permission_ids,
        "null_permissionId_documents": null_permission_ids,
        "invalid_permissionId_references": invalid_permission_refs,
        "duplicate_role_permission_combos": duplicate_role_permission_combos,
        "legacy_permissionCode_mismatches": rp_legacy_mismatches,
    },
    "indexes": {
        "permissions": perm_indexes,
        "roles": role_indexes,
        "role_permissions": rp_indexes,
    },
    "backups": backup_report,
    "generated_at": datetime.utcnow().isoformat() + "Z",
}

print(json.dumps(final_report, default=str, indent=2))
