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

# Users identified with missing companyId/branchId
MISSING_USER_IDS = [
    "6a59da184dd04831201e71ae",
    "6a74348789dd1899f87043c6",
    "6a7475d3457609815c49f054",
    "6a7c20a0fba3d43adb70f9e8",
    "6a7daa38217a40f271d0b3c2",
    "6a7e9874ed79415ae11468fc",
    "6a7f09e082b51d4fe13c3e93",
]

# Role mapping
ROLE_MAP = {
    "Super Admin": "ROLE_SUPER_ADMIN",
    "Employee": "ROLE_EMPLOYEE",
    "Admin": "ROLE_ADMIN",
    "Manager": "ROLE_MANAGER",
    "HR": "ROLE_HR",
    "Accounts": "ROLE_ACCOUNTS",
    "Accounts MD": "ROLE_ACCOUNTS_MD",
}

results = []

users_coll = db["users"]
employees_coll = db["employees"]
companies_coll = db.get_collection("companies") if "companies" in db.list_collection_names() else None
branches_coll = db.get_collection("branches") if "branches" in db.list_collection_names() else None
employment_histories_coll = db.get_collection("employee_employment_histories") if "employee_employment_histories" in db.list_collection_names() else None

for uid in MISSING_USER_IDS:
    # lookup user (ObjectId may be used)
    try:
        oid = ObjectId(uid)
    except Exception:
        oid = uid
    user = users_coll.find_one({"_id": oid})
    if not user:
        continue

    # Extract user fields
    emp_id = user.get("empId")  # also employeeCode
    employee_code = user.get("employeeCode")
    legacy_uuid = user.get("employeeId")
    legacy_role = user.get("role")

    # Special case: bootstrap admin user (empId "0001")
    if emp_id == "0001":
        # Do not attempt employee lookup; treat as system bootstrap user
        employee = None
    else:
        # Resolve employee via empId / employeeCode -> employees.employeeCode (or empId)
        employee = None
        if emp_id:
            employee = employees_coll.find_one({"employeeCode": emp_id})
        if not employee and employee_code:
            employee = employees_coll.find_one({"employeeCode": employee_code})
        # Fallback: try matching by legacyEmployeeUuid directly (should not be primary path)
        if not employee and legacy_uuid:
            employee = employees_coll.find_one({"legacyEmployeeUuid": legacy_uuid})

    employee_verified = False
    employee_rel_status = ""
    canonical_employee_id = None
    company_id = None
    branch_id = None
    context_verified = False
    conflict_msgs = []
    classification = ""
    # Determine if this is the bootstrap admin user
    is_bootstrap = (emp_id == "0001")

    if employee:
        canonical_employee_id = employee.get("employeeId")
        # Verify legacy UUID match
        if legacy_uuid and employee.get("legacyEmployeeUuid") == legacy_uuid:
            employee_verified = True
        else:
            conflict_msgs.append("Legacy UUID mismatch")
        # Verify status and isCurrent
        status = employee.get("status")
        is_current = employee.get("isCurrent")
        if status != "Active":
            conflict_msgs.append(f"Employee status not Active ({status})")
        if not is_current:
            conflict_msgs.append("Employee isCurrent flag false")
        # Extract company/branch from employment subdocument if present
        employment_history = None
        company_id = None
        branch_id = None
        employment_history_id = None
        if employee:
            # Use employee_employment_histories as authoritative source
            emp_hist = employment_histories_coll.find_one({"employeeId": employee.get("employeeId"), "isCurrent": True}) if employment_histories_coll is not None else None
            if emp_hist:
                employment_history = emp_hist
                employment_history_id = emp_hist.get("_id")
                company_id = emp_hist.get("companyId")
                branch_id = emp_hist.get("branchId")
            else:
                conflict_msgs.append("Current employment history not found")
        # Verify referenced collections if they exist
        company_ref_status = "Missing"
        branch_ref_status = "Missing"
        if company_id and companies_coll is not None:
            if companies_coll.find_one({"_id": ObjectId(company_id)}):
                company_ref_status = "Exists"
            else:
                conflict_msgs.append("Company ID does not exist in companies collection")
        if branch_id and branches_coll is not None:
            branch_doc = branches_coll.find_one({"_id": ObjectId(branch_id)})
            if branch_doc:
                branch_ref_status = "Exists"
                branch_company = branch_doc.get("companyId")
                if branch_company and branch_company != company_id:
                    conflict_msgs.append("Branch.companyId does not match employee companyId")
            else:
                conflict_msgs.append("Branch ID does not exist in branches collection")
        if not conflict_msgs:
            context_verified = True
        employee_rel_status = ", ".join(conflict_msgs) if conflict_msgs else "VERIFIED"
    else:
        employee_rel_status = "Employee not found"
        # For bootstrap user, override classification later
        employment_history_id = None
        company_id = None
        branch_id = None
        company_ref_status = "Missing"
        branch_ref_status = "Missing"

    # Resolve canonical roleId
    canonical_role_id = ROLE_MAP.get(legacy_role)
    role_exists = None
    if canonical_role_id:
        role_doc = db["roles"].find_one({"roleId": canonical_role_id})
        role_exists = role_doc is not None
        if not role_exists:
            conflict_msgs.append(f"Canonical roleId {canonical_role_id} not found in roles collection")

    # Determine classification based on gathered info
    if is_bootstrap:
        classification = "SYSTEM_BOOTSTRAP_USER"
        context_verified = True
    elif not employee:
        classification = "EMPLOYEE_NOT_FOUND"
    elif not conflict_msgs:
        classification = "RESOLVED"
    elif any("Current employment history not found" in msg for msg in conflict_msgs):
        classification = "EMPLOYEE_DATA_INCOMPLETE"
    elif any("does not exist" in msg or "does not match" in msg for msg in conflict_msgs):
        classification = "RESOLVED_WITH_REFERENCE_CONFLICT"
    else:
        classification = "AMBIGUOUS"

    results.append({
        "userId": uid,
        "empId": emp_id,
        "employeeCode": employee_code,
        "userEmployeeId": legacy_uuid,
        "employeeId": canonical_employee_id,
        "legacyEmployeeUuid": employee.get("legacyEmployeeUuid") if employee else None,
        "employeeVerified": employee_verified,
        "employmentHistoryId": employment_history_id,
        "companyId": company_id,
        "branchId": branch_id,
        "companyReferenceStatus": company_ref_status if company_id else "Missing",
        "branchReferenceStatus": branch_ref_status if branch_id else "Missing",
        "legacyRole": legacy_role,
        "canonicalRoleId": canonical_role_id,
        "roleExists": role_exists,
        "employeeRelationStatus": employee_rel_status,
        "contextVerified": context_verified,
        "classification": classification,
        "conflicts": conflict_msgs,
    })

# Write markdown report
md_path = r"c:/ess/ess_sample_2/backend/docs/phase4_user_context_forensic_report.md"
with open(md_path, "w", encoding="utf-8") as md:
    md.write("# Phase 4 – User Context Forensic Report\n\n")
    md.write("| userId | empId | employeeCode | userEmployeeId | employeeId | legacyEmployeeUuid | employeeVerified | employmentHistoryId | companyId | branchId | companyReferenceStatus | branchReferenceStatus | legacyRole | canonicalRoleId | roleExists | employeeRelationStatus | contextVerified | classification |\n")
    md.write("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
    for r in results:
        md.write(
            f"| {r['userId']} | {r.get('empId') or ''} | {r.get('employeeCode') or ''} | {r.get('userEmployeeId') or ''} | {r.get('employeeId') or ''} | {r.get('legacyEmployeeUuid') or ''} | {r['employeeVerified']} | {r.get('employmentHistoryId') or ''} | {r.get('companyId') or ''} | {r.get('branchId') or ''} | {r.get('companyReferenceStatus') or ''} | {r.get('branchReferenceStatus') or ''} | {r.get('legacyRole') or ''} | {r.get('canonicalRoleId') or ''} | {r.get('roleExists')} | {r.get('employeeRelationStatus')} | {r['contextVerified']} | {r.get('classification')} |\n"
        )

# Write JSON backup
json_path = r"c:/ess/ess_sample_2/backend/backups/phase4_user_context_forensic_v3.json"
with open(json_path, "w", encoding="utf-8") as jf:
    # Convert any ObjectId values to strings for JSON serialization
    serializable_results = []
    for rec in results:
        rec_copy = rec.copy()
        for k, v in rec_copy.items():
            if isinstance(v, ObjectId):
                rec_copy[k] = str(v)
        serializable_results.append(rec_copy)
    json.dump({"timestamp": datetime.utcnow().isoformat(), "results": serializable_results}, jf, indent=2)

print(f"Forensic markdown report written to {md_path}")
print(f"JSON backup written to {json_path}")
