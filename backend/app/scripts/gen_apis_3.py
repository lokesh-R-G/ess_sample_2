import os
import json
from pathlib import Path

ARTIFACTS_DIR = Path(r"C:\Users\dell\.gemini\antigravity-ide\brain\0093acac-024f-4ad3-8651-7c86d23f77d2")

def generate_endpoint(ep):
    return f"""## {ep['name']}

**1. API Name:** {ep['name']}
**2. Route:** `{ep['route']}`
**3. HTTP Method:** `{ep['method']}`
**4. Version:** `v2`
**5. Description:** {ep['desc']}
**6. Business Capability:** {ep['capability']}
**7. Business Owner:** {ep['owner']}
**8. Consumers:** {ep['consumers']}

### Business Scenario
{ep['scenario']}

### Authorization
- **Allowed Roles:** {ep['auth']}
- **Reason:** {ep['auth_reason']}

### Request Contract
```json
{json.dumps(ep['req'], indent=2)}
```
*Field Details:*
{chr(10).join([f"- `{k}`: {v}" for k, v in ep['req_details'].items()])}

### Response Contract
```json
{json.dumps(ep['res'], indent=2)}
```

### Business Workflow
```text
{ep['workflow']}
```

### Business Rules
{chr(10).join([f"- {r}" for r in ep['rules']])}

### Validation Rules
{chr(10).join([f"- {r}" for r in ep['validations']])}

### Error Codes
{chr(10).join([f"- **{e['code']}**: {e['meaning']} (Fix: {e['fix']})" for e in ep['errors']])}

### Events
- **Published:** `{ep['event']}`
- **Payload:** `{ep['event_payload']}`
- **Consumers:** {ep['event_consumers']}

### Transaction Design
- **Type:** {ep['transaction']}
- **Idempotency:** {ep['idempotency']}

### Downstream Integrations
{ep['downstream']}

### Audit
{ep['audit']}

### Example End-to-End Flow
{ep['e2e']}

---
"""

def write_doc(filename, title, endpoints):
    content = f"# {title}\n\n"
    for ep in endpoints:
        content += generate_endpoint(ep)
    with open(ARTIFACTS_DIR / filename, "w", encoding="utf-8") as f:
        f.write(content)


# ==========================================
# LEAVE ENGINE
# ==========================================
leave_endpoints = [
    {
        "name": "Process Attendance Penalty",
        "route": "/api/v2/leave/process-penalty",
        "method": "POST",
        "desc": "Consumes pending attendance penalties and attempts to deduct from available leave balances via waterfall rules.",
        "capability": "Automated Consequence Management",
        "owner": "System",
        "consumers": "Payroll",
        "scenario": "The Attendance Engine detects 4 late comings and issues a 'Half Day Penalty'. This API looks at the Leave Conversion Policy, checks if the employee has Casual Leave (CL). If yes, it deducts 0.5 CL. If not, it deducts Earned Leave (EL). If empty, it marks Loss of Pay (LOP).",
        "auth": "SYSTEM",
        "auth_reason": "Triggered autonomously via the AttendancePenaltyLedger queue. No human intervention.",
        "req": {
            "penaltyId": "PEN-44921",
            "employeeId": "EMP000145",
            "penaltyType": "LATE_THRESHOLD",
            "amountDeduction": 0.5
        },
        "req_details": {
            "penaltyId": "Required. Reference to the Attendance ledger entry."
        },
        "res": {
            "success": True,
            "deductedFrom": "CASUAL_LEAVE",
            "ledgerId": "L-LDG-993",
            "status": "PROCESSED",
            "publishedEvents": ["LeavePenaltyApplied"]
        },
        "workflow": "Fetch Pending Penalty -> Fetch Leave Conversion Policy waterfall -> Check Balance(CL) -> Balance is > 0.5 -> Insert Ledger entry -0.5 CL -> Mark Penalty as Processed.",
        "rules": [
            "Balances are never modified directly; debits are inserted into LeaveLedger.",
            "Waterfall logic strictly obeys the priority defined in LeavePolicyEngine."
        ],
        "validations": [
            "Penalty must be in PENDING state.",
            "Employee must be Active."
        ],
        "errors": [
            {"code": "PENALTY_ALREADY_PROCESSED", "meaning": "Duplication protection.", "fix": "Ignore."},
            {"code": "NO_VALID_POLICY", "meaning": "Waterfall mapping missing.", "fix": "HR must configure Leave Conversion Rules."}
        ],
        "event": "LeavePenaltyApplied",
        "event_payload": "{ employeeId, leaveType, amount }",
        "event_consumers": "Payroll Engine (if LOP occurred)",
        "transaction": "Atomic insertion into LeaveLedger and update of PenaltyLedger.",
        "idempotency": "Strict checking on penaltyId ensures double-deductions never happen.",
        "downstream": "Alerts Payroll ONLY if the waterfall exhausts all paid leave and defaults to LOP.",
        "audit": "System IP, Timestamp.",
        "e2e": "Attendance flags late -> Penalty Pushed -> Leave Engine pulls penalty -> Deducts CL -> Writes Ledger -> Done."
    }
]

if __name__ == "__main__":
    write_doc("08_Leave_Policy_Business_API.md", "Leave Policy Engine Business APIs", [])
    write_doc("09_Leave_Business_API.md", "Leave Engine Business APIs", leave_endpoints)
    print("Leave Generated.")
