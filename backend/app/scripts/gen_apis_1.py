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
# ORGANIZATION ENGINE
# ==========================================
org_endpoints = [
    {
        "name": "Create Company",
        "route": "/api/v2/organization/company/create",
        "method": "POST",
        "desc": "Registers a new legal corporate entity into the HRMS.",
        "capability": "Legal Entity Management",
        "owner": "Super Admin",
        "consumers": "All Engines",
        "scenario": "A conglomerate acquires a new subsidiary. The Super Admin creates the new company profile to begin onboarding its respective branches, departments, and employees.",
        "auth": "SUPER_ADMIN",
        "auth_reason": "Company creation dictates legal compliance, tax tracking, and billing boundaries. Only the absolute highest authority can create a root tenant.",
        "req": {
            "companyName": "Acme Global Solutions Pvt Ltd",
            "registrationCode": "CIN-U72900KA2026PTC123456",
            "incorporationDate": "2026-01-15",
            "baseCurrency": "INR",
            "taxIdentifier": "29AAACA1234A1Z5",
            "financialYearStartMonth": 4
        },
        "req_details": {
            "companyName": "Required. Full legal name.",
            "registrationCode": "Required. Official government registration string.",
            "baseCurrency": "Required. ISO currency code for payroll baseline."
        },
        "res": {
            "success": True,
            "transactionId": "TXN-ORG-9921",
            "companyId": "CMP-0012",
            "status": "DRAFT",
            "publishedEvents": ["CompanyRegistered"]
        },
        "workflow": "Validate Registration Code Unique -> Validate Currency -> Insert Company Document -> Create Root Admin Role -> Publish Event.",
        "rules": [
            "Company name must be legally distinct.",
            "A newly created company is in DRAFT status and cannot accept employees until activated."
        ],
        "validations": [
            "registrationCode must not exist globally.",
            "financialYearStartMonth must be between 1 and 12."
        ],
        "errors": [
            {"code": "COMPANY_DUPLICATE_REGISTRATION", "meaning": "Tax ID exists.", "fix": "Verify if the subsidiary is already registered."},
            {"code": "INVALID_CURRENCY_CODE", "meaning": "Currency not ISO standard.", "fix": "Use USD, INR, EUR, etc."}
        ],
        "event": "CompanyRegistered",
        "event_payload": "{ companyId, currency, name }",
        "event_consumers": "Billing Engine, Audit Engine",
        "transaction": "Atomic. Rolls back if root role creation fails.",
        "idempotency": "Idempotency-Key header supported. Retries safely return existing companyId.",
        "downstream": "Alerts Billing Engine to start subscription tracking.",
        "audit": "Logs Admin IP, Timestamp, and entire JSON payload.",
        "e2e": "Admin creates Acme Global -> Company stored -> Billing activated -> Ready for Branch creation."
    },
    {
        "name": "Transfer Branch",
        "route": "/api/v2/organization/branch/transfer",
        "method": "POST",
        "desc": "Moves an existing physical branch from one Company to another.",
        "capability": "Corporate Restructuring",
        "owner": "Super Admin",
        "consumers": "Employee Engine",
        "scenario": "A spin-off occurs. Branch 'Bangalore R&D' is moved from Company A to newly created Company B. All employees mapped to this branch must logically fall under Company B.",
        "auth": "SUPER_ADMIN",
        "auth_reason": "Transferring a branch alters the legal employer for hundreds of employees simultaneously.",
        "req": {
            "branchId": "BR-009",
            "targetCompanyId": "CMP-002",
            "effectiveDate": "2026-04-01",
            "transferReason": "Corporate Spin-off",
            "autoMigrateEmployees": True
        },
        "req_details": {
            "branchId": "Required. Existing branch.",
            "targetCompanyId": "Required. Active destination company."
        },
        "res": {
            "success": True,
            "transactionId": "TXN-ORG-9988",
            "employeesImpacted": 450,
            "publishedEvents": ["BranchTransferred", "MassEmployeeTransferInitiated"]
        },
        "workflow": "Lock Branch -> Validate Target Company -> Update Branch companyId -> Generate Mass Transfer Job for Employee Engine -> Publish Events.",
        "rules": [
            "Branch cannot be transferred if payroll is currently processing.",
            "If autoMigrateEmployees is True, Employee Engine assumes ownership of migration."
        ],
        "validations": [
            "Target Company must be ACTIVE.",
            "Effective Date cannot be in a closed financial period."
        ],
        "errors": [
            {"code": "PAYROLL_LOCK_ACTIVE", "meaning": "Payroll is running.", "fix": "Wait until payroll is closed."},
            {"code": "TARGET_COMPANY_INACTIVE", "meaning": "Cannot transfer to a draft company.", "fix": "Activate the company first."}
        ],
        "event": "BranchTransferred",
        "event_payload": "{ branchId, oldCompanyId, newCompanyId, effectiveDate }",
        "event_consumers": "Employee Engine, Attendance Engine",
        "transaction": "Distributed Saga. Organization Engine updates branch, Employee Engine asynchronously updates 450 employees.",
        "idempotency": "Strict checking on effectiveDate and targetCompanyId.",
        "downstream": "Employee Engine initiates mass historical assignment updates.",
        "audit": "Logs old company ID, new company ID, and Admin ID.",
        "e2e": "Admin submits transfer -> Org Engine updates branch -> Employee Engine receives event -> 450 employees get new assignments -> Salary Engine notified of entity change."
    }
]

# ==========================================
# EMPLOYEE ENGINE
# ==========================================
emp_endpoints = [
    {
        "name": "Promote Employee",
        "route": "/api/v2/employee/promote",
        "method": "POST",
        "desc": "Executes an official promotion, updating designation, department, reporting lines, and triggering salary revisions.",
        "capability": "Lifecycle Management",
        "owner": "HR Admin",
        "consumers": "Salary Engine, Payroll",
        "scenario": "Annual appraisal is finalized. An employee is promoted from 'Software Engineer' to 'Senior Software Engineer', moved to a new team, and given a 15% hike.",
        "auth": "HR_ADMIN",
        "auth_reason": "Promotions alter legal compensation and organizational hierarchy.",
        "req": {
            "employeeId": "EMP000145",
            "newDesignationId": "DES005",
            "newDepartmentId": "DEP003",
            "reportingManagerId": "EMP000010",
            "effectiveDate": "2026-08-01",
            "promotionReason": "Annual Performance Review",
            "salaryRevisionRequested": True
        },
        "req_details": {
            "employeeId": "Required.",
            "newDesignationId": "Required. Must exist in Org Engine.",
            "effectiveDate": "Required. Future or current date."
        },
        "res": {
            "success": True,
            "transactionId": "TXN-EMP-4432",
            "employeeId": "EMP000145",
            "assignmentId": "ASN-992",
            "status": "PROMOTION_SCHEDULED",
            "publishedEvents": ["EmployeePromoted", "SalaryRevisionRequested"]
        },
        "workflow": "Validate Employee Active -> Validate Designation/Dept exists in Org -> Archive current Assignment -> Create new Assignment -> Publish SalaryRevisionRequested -> Notify Manager.",
        "rules": [
            "Promotion cannot use an inactive designation.",
            "Promotion automatically closes previous reporting relationship.",
            "Historical assignment data is immutable and retained."
        ],
        "validations": [
            "Effective date cannot overlap a future scheduled assignment.",
            "Reporting manager cannot be the employee themselves."
        ],
        "errors": [
            {"code": "ASSIGNMENT_OVERLAP", "meaning": "A future assignment already exists.", "fix": "Cancel the future transfer/promotion first."},
            {"code": "CIRCULAR_REPORTING_LINE", "meaning": "Manager reports to this employee.", "fix": "Select a valid higher-level manager."}
        ],
        "event": "EmployeePromoted",
        "event_payload": "{ employeeId, oldDesignation, newDesignation, effectiveDate }",
        "event_consumers": "Salary Engine, Workflow Engine",
        "transaction": "MongoDB Atomic Transaction. Old assignment end-dated and new assignment created simultaneously.",
        "idempotency": "Idempotent. Re-submitting same effectiveDate and Designation returns existing assignmentId.",
        "downstream": "Salary Engine listens to `SalaryRevisionRequested` to open a draft CTC revision for HR.",
        "audit": "Captures HR User ID, old designation, new designation, and exact timestamp.",
        "e2e": "HR promotes employee -> Assignment updated -> Event fires -> Salary Engine opens draft revision -> HR approves salary -> ESS notified."
    },
    {
        "name": "Resign Employee",
        "route": "/api/v2/employee/resign",
        "method": "POST",
        "desc": "Initiates the separation workflow, calculating notice periods and locking future leave applications.",
        "capability": "Separation Management",
        "owner": "Employee / HR",
        "consumers": "Leave Engine, Payroll",
        "scenario": "An employee submits their resignation via the portal. The system calculates their 60-day notice period and alerts the manager.",
        "auth": "EMPLOYEE, HR",
        "auth_reason": "Employees initiate their own resignation. HR initiates forced separations.",
        "req": {
            "employeeId": "EMP000145",
            "resignationDate": "2026-07-25",
            "requestedRelievingDate": "2026-09-23",
            "reasonCategory": "Career Growth",
            "comments": "Moving to a different city."
        },
        "req_details": {
            "requestedRelievingDate": "Required. Evaluated against policy."
        },
        "res": {
            "success": True,
            "resignationId": "RES-001",
            "noticePeriodShortfallDays": 0,
            "status": "PENDING_APPROVAL",
            "publishedEvents": ["ResignationSubmitted"]
        },
        "workflow": "Verify Employee Active -> Calculate Policy Notice Period -> Compare with requested date -> Calculate Shortfall -> Create Resignation Record -> Trigger Approval Workflow.",
        "rules": [
            "Employee cannot apply for leave beyond the requested relieving date.",
            "Shortfall days are flagged for Payroll recovery."
        ],
        "validations": [
            "Employee must not already have an active resignation.",
            "Resignation date cannot be in the future."
        ],
        "errors": [
            {"code": "ALREADY_RESIGNED", "meaning": "Resignation exists.", "fix": "Track existing workflow."},
            {"code": "BOND_PERIOD_ACTIVE", "meaning": "Employee is under a training bond.", "fix": "HR intervention required for buyout."}
        ],
        "event": "ResignationSubmitted",
        "event_payload": "{ employeeId, requestedDate, shortfallDays }",
        "event_consumers": "Workflow Engine, Leave Engine",
        "transaction": "Atomic insertion of separation record.",
        "idempotency": "Fails cleanly with ALREADY_RESIGNED.",
        "downstream": "Leave Engine blocks future leave. Workflow routes to Manager.",
        "audit": "IP Address of submission captured.",
        "e2e": "Employee resigns -> Notice evaluated -> Leave Engine locks future dates -> Manager approves -> Status changes to SERVING_NOTICE."
    }
]

if __name__ == "__main__":
    write_doc("01_Organization_Business_API.md", "Organization Engine Business APIs", org_endpoints)
    write_doc("02_Employee_Business_API.md", "Employee Engine Business APIs", emp_endpoints)
    print("Org & Emp Generated.")
