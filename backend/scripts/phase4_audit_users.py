import sys
import os
import json
from datetime import datetime
from pymongo import MongoClient
# Ensure backend package is on sys.path for imports
sys.path.append(r"c:/ess/ess_sample_2/backend")
from app.core.config import get_settings

# Ensure project root on sys.path for imports
sys.path.append(r"c:/ess/ess_sample_2/backend")
sys.path.append(r"c:/ess/ess_sample_2")

settings = get_settings()
client = MongoClient(settings.mongo_uri)
db = client[settings.mongo_db_name]

audit_dir = r"c:/ess/ess_sample_2/backend/backups/phase4_audit"
os.makedirs(audit_dir, exist_ok=True)

users_coll = db['users']
users = list(users_coll.find())

# Prepare audit data
audit_data = []
legacy_roles = set()
missing_company = []
missing_branch = []
for u in users:
    entry = {
        "_id": str(u.get("_id")),
        "empId": u.get("empId"),
        "role": u.get("role"),
        "roleId": u.get("roleId"),
        "authorizationVersion": u.get("authorizationVersion"),
        "companyId": u.get("companyId"),
        "branchId": u.get("branchId"),
    }
    audit_data.append(entry)
    if u.get("role"):
        legacy_roles.add(u.get("role"))
    if not u.get("companyId"):
        missing_company.append(entry["_id"])
    if not u.get("branchId"):
        missing_branch.append(entry["_id"])

audit_path = os.path.join(audit_dir, "users_audit.json")
with open(audit_path, "w", encoding="utf-8") as f:
    json.dump({
        "timestamp": datetime.utcnow().isoformat(),
        "legacy_roles": list(legacy_roles),
        "missing_companyId_user_ids": missing_company,
        "missing_branchId_user_ids": missing_branch,
        "users": audit_data,
    }, f, indent=2)

print(f"Audit completed. Legacy roles: {list(legacy_roles)}")
print(f"Missing companyId user IDs: {missing_company}")
print(f"Missing branchId user IDs: {missing_branch}")
print(f"Audit file written to {audit_path}")
