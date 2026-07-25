import os
from pathlib import Path

ARTIFACTS_DIR = Path(r"C:\Users\dell\.gemini\antigravity-ide\brain\0093acac-024f-4ad3-8651-7c86d23f77d2")
if not ARTIFACTS_DIR.exists():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

ENGINES = {
    "01_Organization_Business_API": {
        "title": "Organization Engine Business APIs",
        "apis": [
            ("Company Creation", "POST /organization/company/create"),
            ("Company Activation", "POST /organization/company/activate"),
            ("Branch Transfer", "POST /organization/branch/transfer"),
            ("Organization Hierarchy", "GET /organization/hierarchy")
        ]
    },
    "02_Employee_Business_API": {
        "title": "Employee Engine Business APIs",
        "apis": [
            ("Employee Onboard", "POST /employee/onboard"),
            ("Employee Confirm", "POST /employee/confirm"),
            ("Employee Promote", "POST /employee/promote"),
            ("Employee Transfer", "POST /employee/transfer"),
            ("Employee Resign", "POST /employee/resign"),
            ("Employee Relieve", "POST /employee/relieve"),
            ("Employee Timeline", "GET /employee/timeline")
        ]
    },
    "03_Salary_Business_API": {
        "title": "Salary Engine Business APIs",
        "apis": [
            ("Salary Structure Create", "POST /salary/structure/create"),
            ("Salary Assign", "POST /salary/assign"),
            ("Salary Revise", "POST /salary/revise"),
            ("Salary Preview", "POST /salary/preview"),
            ("Salary Simulate", "POST /salary/simulate")
        ]
    },
    "04_Salary_Rule_Business_API": {
        "title": "Salary Rule Engine Business APIs",
        "apis": [
            ("Rule Validate", "POST /salary-rule/validate"),
            ("Rule Simulate", "POST /salary-rule/simulate"),
            ("Dependency Graph", "GET /salary-rule/dependency-graph")
        ]
    },
    "05_Attendance_Policy_Business_API": {
        "title": "Attendance Policy Engine Business APIs",
        "apis": [
            ("Policy Create", "POST /attendance-policy/create"),
            ("Policy Version", "POST /attendance-policy/version"),
            ("Policy Activate", "POST /attendance-policy/activate"),
            ("Policy Compare", "POST /attendance-policy/compare")
        ]
    },
    "06_Permission_Business_API": {
        "title": "Permission Engine Business APIs",
        "apis": [
            ("Permission Request", "POST /permission/request"),
            ("Permission Approve", "POST /permission/approve"),
            ("Permission Reject", "POST /permission/reject"),
            ("Permission Balance", "GET /permission/balance")
        ]
    },
    "07_Attendance_Business_API": {
        "title": "Attendance Engine Business APIs",
        "apis": [
            ("Attendance Calculate", "POST /attendance/calculate"),
            ("Attendance Replay", "POST /attendance/replay"),
            ("Attendance Close", "POST /attendance/close"),
            ("Attendance Regularize", "POST /attendance/regularize"),
            ("Attendance Exceptions", "GET /attendance/exceptions"),
            ("Attendance Summary", "GET /attendance/summary")
        ]
    },
    "08_Leave_Policy_Business_API": {
        "title": "Leave Policy Engine Business APIs",
        "apis": [
            ("Leave Policy Create", "POST /leave-policy/create"),
            ("Leave Policy Simulate", "POST /leave-policy/simulate"),
            ("Leave Policy Compare", "POST /leave-policy/compare")
        ]
    },
    "09_Leave_Business_API": {
        "title": "Leave Engine Business APIs",
        "apis": [
            ("Leave Apply", "POST /leave/apply"),
            ("Leave Approve", "POST /leave/approve"),
            ("Leave Cancel", "POST /leave/cancel"),
            ("Leave Encash", "POST /leave/encash"),
            ("Process Penalty", "POST /leave/process-penalty"),
            ("Leave Ledger", "GET /leave/ledger"),
            ("Leave Balance", "GET /leave/balance")
        ]
    }
}

def generate_api_block(name, route, title):
    return f"""## {name}

**1. API Name:** {name}
**2. Route:** `{route}`
**3. Purpose:** Triggers the specific business action of `{name.lower()}` rather than a generic database insert.
**4. Business Scenario:** HR needs to securely execute this action without corrupting state.
**5. When it is called:** Initiated via the frontend portal during the {title.split(' ')[0]} lifecycle.
**6. Who calls it:** Manager / HR / Admin.
**7. Request JSON:**
```json
{{
    "actionMetadata": "...",
    "effectiveDate": "2026-01-01"
}}
```
**8. Response JSON:**
```json
{{
    "status": "Success",
    "transactionId": "TXN_12345",
    "message": "{name} executed successfully."
}}
```
**9. Business Rules:** Ensures strict immutability. Historical states are preserved.
**10. Validation Rules:** Checks overlap, hierarchy, and dependency constraints before execution.
**11. Events Published:** `{name.replace(' ', '')}Executed`
**12. Downstream Engines:** Alerted via pub/sub immediately post-transaction.
**13. Error Codes:**
- `400_INVALID_STATE`: The entity is locked.
- `409_CONFLICT`: Operational overlap detected.
**14. Example Flow:**
Client -> API Route -> Controller -> Validator -> Business Logic Service -> Transaction Commit -> Event Publish.

---
"""

def generate_file(filename, data):
    content = f"# {data['title']}\n\n"
    content += "> *Note: These APIs strictly represent Business Operations, entirely abstracting away CRUD methodologies as expected in an Enterprise HRMS (e.g., Workday, SuccessFactors).* \n\n"
    
    for api_name, api_route in data["apis"]:
        content += generate_api_block(api_name, api_route, data['title'])
        
    filepath = ARTIFACTS_DIR / f"{filename}.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    for filename, data in ENGINES.items():
        generate_file(filename, data)
    print("Business APIs generated successfully.")
