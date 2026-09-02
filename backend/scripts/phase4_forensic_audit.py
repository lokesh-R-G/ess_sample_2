import sys
import os
import json
from datetime import datetime
from pymongo import MongoClient
# Ensure backend package is on sys.path for imports
sys.path.append(r"c:/ess/ess_sample_2/backend")
from app.core.config import get_settings

settings = get_settings()
client = MongoClient(settings.mongo_uri)
db = client[settings.mongo_db_name]

# Users with missing companyId/branchId (from previous audit)
missing_user_ids = [
    "6a59da184dd04831201e71ae",
    "6a74348789dd1899f87043c6",
    "6a7475d3457609815c49f054",
    "6a7c20a0fba3d43adb70f9e8",
    "6a7daa38217a40f271d0b3c2",
    "6a7e9874ed79415ae11468fc",
    "6a7f09e082b51d4fe13c3e93",
]

results = []

users_coll = db['users']
# Access related collections (may be empty if not present)
employees_coll = db['employees']
organizations_coll = db['organizations']
branches_coll = db['branches']

for uid in missing_user_ids:
    user = users_coll.find_one({"_id": uid})
    if not user:
        continue
    emp_id = user.get('empId')
    legacy_role = user.get('role')
    company_id = None
    branch_id = None
    source = None
    employee = None
    if emp_id:
        employee = employees_coll.find_one({"empId": emp_id})
        if not employee:
            employee = employees_coll.find_one({"employeeId": emp_id})
    if employee:
        company_id = employee.get('companyId') or employee.get('organizationId')
        branch_id = employee.get('branchId')
        source = f"employees collection (empId={emp_id})"
    if not company_id:
        if 'organizationId' in user:
            company_id = user.get('organizationId')
            source = 'user.organizationId'
        elif 'companyId' in user:
            company_id = user.get('companyId')
            source = 'user.companyId'
    if not branch_id and 'branchId' in user:
        branch_id = user.get('branchId')
        source = source or 'user.branchId'
    results.append({
        "userId": uid,
        "empId": emp_id,
        "legacyRole": legacy_role,
        "companyId": company_id,
        "branchId": branch_id,
        "source": source
    })

output_path = r"c:/ess/ess_sample_2/backend/backups/phase4_forensic_audit.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({"timestamp": datetime.utcnow().isoformat(), "results": results}, f, indent=2)

print(f"Forensic audit written to {output_path}")
