import os, sys, json
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

# Ensure backend root is on sys.path for internal imports
project_root = os.path.abspath('C:/ess/ess_sample_2/backend')
sys.path.append(project_root)

from app.core.config import get_settings

# Expected role mapping for the five production users (empId -> roleId)
EXPECTED_ROLE_MAP = {
    "5188": "ROLE_SUPER_ADMIN",
    "202201": "ROLE_EMPLOYEE",
    "202102": "ROLE_EMPLOYEE",
    "1021": "ROLE_EMPLOYEE",
    "5182": "ROLE_EMPLOYEE",
}

settings = get_settings()
client = MongoClient(settings.mongo_uri.strip())
db = client[settings.mongo_db_name.strip()]

users_coll = db["users"]
log_coll = db["phase4_user_migration_log"]

# Gather verification data
verification = {
    "user_checks": [],
    "log_count": log_coll.count_documents({}),
    "log_entries": [],
}

for user in users_coll.find({}):
    emp_id = user.get("empId")
    entry = {
        "userId": str(user.get("_id")),
        "empId": emp_id,
        "roleId": user.get("roleId"),
        "authorizationVersion": user.get("authorizationVersion"),
        "legacyRole": user.get("role"),
    }
    # For production users, check expected role & auth version
    if emp_id and emp_id not in ("0001",) and not str(emp_id).startswith("TEST-"):
        expected_role = EXPECTED_ROLE_MAP.get(emp_id)
        entry["expectedRole"] = expected_role
        entry["roleMatch"] = (user.get("roleId") == expected_role)
        entry["authVersionMatch"] = (user.get("authorizationVersion") == 1)
    verification["user_checks"].append(entry)

# Capture log entries details
for log in log_coll.find({}):
    verification["log_entries"].append({
        "userId": str(log.get("userId")),
        "prevRoleId": log.get("prevRoleId"),
        "newRoleId": log.get("newRoleId"),
        "prevAuthVersion": log.get("prevAuthVersion"),
        "newAuthVersion": log.get("newAuthVersion"),
        "changedBy": log.get("changedBy"),
    })

print(json.dumps(verification, default=str, indent=2))
