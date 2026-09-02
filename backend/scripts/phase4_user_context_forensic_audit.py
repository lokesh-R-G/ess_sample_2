import sys
import os
import json
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

# Ensure backend package is importable
sys.path.append(r"c:/ess/ess_sample_2/backend")
from app.core.config import get_settings

settings = get_settings()
client = MongoClient(settings.mongo_uri)
db = client[settings.mongo_db_name]

# List of user IDs previously identified as missing companyId/branchId
MISSING_USER_IDS = [
    "6a59da184dd04831201e71ae",
    "6a74348789dd1899f87043c6",
    "6a7475d3457609815c49f054",
    "6a7c20a0fba3d43adb70f9e8",
    "6a7daa38217a40f271d0b3c2",
    "6a7e9874ed79415ae11468fc",
    "6a7f09e082b51d4fe13c3e93",
]

results = []

users_coll = db["users"]
employees_coll = db["employees"]
employment_hist_coll = db["employee_employment_histories"]

for uid in MISSING_USER_IDS:
    try:
        oid = ObjectId(uid)
    except Exception:
        oid = uid
    user = users_coll.find_one({"_id": oid})
    if not user:
        continue
    emp_code = user.get("empId")
    employee_uuid = user.get("employeeId")
    legacy_role = user.get("role")
    company_id = None
    branch_id = None
    source = None

    # First try employment history (authoritative source)
    if employee_uuid:
        emp_hist = employment_hist_coll.find_one({"employeeId": employee_uuid, "isCurrent": True})
        if emp_hist:
            company_id = emp_hist.get("companyId") or emp_hist.get("organizationId")
            branch_id = emp_hist.get("branchId")
            source = "employee_employment_histories (isCurrent)"
    # Fallback to employees collection if not found above
    if not company_id and not branch_id:
        if employee_uuid:
            employee = employees_coll.find_one({"employeeId": employee_uuid})
        elif emp_code:
            employee = employees_coll.find_one({"empId": emp_code})
        else:
            employee = None
        if employee:
            company_id = employee.get("companyId") or employee.get("organizationId")
            branch_id = employee.get("branchId")
            source = "employees collection"
    # Final fallback to fields directly on user document
    if not company_id:
        if "organizationId" in user:
            company_id = user.get("organizationId")
            source = source or "user.organizationId"
        elif "companyId" in user:
            company_id = user.get("companyId")
            source = source or "user.companyId"
    if not branch_id and "branchId" in user:
        branch_id = user.get("branchId")
        source = source or "user.branchId"

    results.append({
        "userId": uid,
        "empId": emp_code,
        "employeeId": employee_uuid,
        "legacyRole": legacy_role,
        "companyId": company_id,
        "branchId": branch_id,
        "source": source,
    })

# Write markdown report
md_path = r"c:/ess/ess_sample_2/backend/docs/phase4_user_context_forensic_report.md"
with open(md_path, "w", encoding="utf-8") as md_file:
    md_file.write("# Phase 4 – User Context Forensic Report\n\n")
    md_file.write("This report resolves `companyId` and `branchId` for users that were missing these fields.\n\n")
    md_file.write("| User ID | Emp Code | Employee UUID | Legacy Role | Company ID | Branch ID | Source |\n")
    md_file.write("|---|---|---|---|---|---|---|\n")
    for r in results:
        md_file.write(f"| {r['userId']} | {r.get('empId') or ''} | {r.get('employeeId') or ''} | {r.get('legacyRole') or ''} | {r.get('companyId') or ''} | {r.get('branchId') or ''} | {r.get('source') or ''} |\n")

# Also write JSON backup for reference
json_path = r"c:/ess/ess_sample_2/backend/backups/phase4_user_context_forensic.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump({"timestamp": datetime.utcnow().isoformat(), "results": results}, f, indent=2)

print(f"Forensic markdown report written to {md_path}")
print(f"JSON backup written to {json_path}")
