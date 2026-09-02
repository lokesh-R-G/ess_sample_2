import os
from pathlib import Path

ARTIFACTS_DIR = Path(r"C:\Users\dell\.gemini\antigravity-ide\brain\0093acac-024f-4ad3-8651-7c86d23f77d2")
if not ARTIFACTS_DIR.exists():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

ENGINES = [
    {
        "filename": "01_Organization_Business_Guide",
        "title": "Organization Engine",
        "purpose": "Stores and manages the legal and hierarchical entity structure of the enterprise.",
        "solves": "Provides a unified source of truth for all corporate structures (Companies, Branches, Departments) ensuring downstream engines don't duplicate foundational entity tracking.",
        "why_not_others": "If Payroll or Attendance managed locations, data would instantly desync. Centralizing Organization data ensures a single point of configuration.",
        "owners": ["Admin (Setup structure)", "HR (Assign employees)", "System (Routes approvals based on structure)"],
        "modules": ["Company Master", "Branch Master", "Department Master", "Designation Master"],
        "rules": ["Every employee must belong to a Company.", "A Branch must belong to a Company.", "Designations map to Departments."],
        "decisions": ["Provides the strict lookup for geographical and hierarchical limits."],
        "never": ["Never manages employees directly.", "Never calculates salary or taxes.", "Never tracks daily attendance."],
        "inputs": ["Entity creation data from Admin/HR."],
        "outputs": ["Company, Branch, Department, Designation profiles."],
        "dependencies": "No upstream dependencies. Consumed by Employee, Salary, Attendance, and Leave.",
        "scenarios": "HR opens a new regional office -> HR creates Branch -> Maps to Company -> Creates Departments -> Branch is ready for Employee Engine assignment."
    },
    {
        "filename": "02_Employee_Business_Guide",
        "title": "Employee Engine",
        "purpose": "Manages employee identity, lifecycle, and assignments within the organization.",
        "solves": "Solves the tracking of an employee's journey (joining, probation, transfer, promotion, exit) with strict historical accuracy.",
        "why_not_others": "Separates biological/demographic identity from payroll numbers or attendance punch times. An employee exists even if they haven't punched in yet.",
        "owners": ["HR (Onboarding/Transfers)", "Employee (Viewing profile)", "Manager (Viewing team)"],
        "modules": ["Employee Profile", "Employment History", "Employee Assignment"],
        "rules": ["Transfers must maintain a historical log.", "An employee can only have one active assignment at a time.", "Exit date terminates active assignment."],
        "decisions": ["Determines the active Reporting Manager.", "Determines the active Branch and Department."],
        "never": ["Never calculates salary components.", "Never evaluates leave policies.", "Never modifies Organization master data."],
        "inputs": ["Organization lookup data, Onboarding forms, Transfer requests."],
        "outputs": ["Employee Master Record, Employment History."],
        "dependencies": "Consumes Organization Engine. Produces for Salary, Attendance, Leave.",
        "scenarios": "Employee gets promoted -> HR initiates Promotion -> Engine archives old Assignment -> Engine creates new Assignment linked to new Designation -> Salary Engine alerted."
    },
    {
        "filename": "03_Salary_Business_Guide",
        "title": "Salary Engine",
        "purpose": "Manages employee compensation structures and historical salary revisions.",
        "solves": "Abstracts away hardcoded pay scales, allowing HR to map mathematical formula structures to employees dynamically.",
        "why_not_others": "Payroll handles the monthly 'run'. Salary Engine handles the 'blueprint'. Keeping blueprints separated means you can forecast salaries without running payroll.",
        "owners": ["HR (Structure Definition)", "Payroll Admin (Execution)", "Employee (Payslip viewing)"],
        "modules": ["SalaryComponent", "SalaryStructure", "EmployeeSalary"],
        "rules": ["Salary structures are versioned.", "Employee salary overrides cannot violate component rules.", "Revisions never overwrite past compensation."],
        "decisions": ["What the active CTC is.", "What the base component allowances are prior to leave deduction."],
        "never": ["Never runs the monthly payroll batch.", "Never deducts leave penalties (Attendance does).", "Never modifies the employee demographic."],
        "inputs": ["Employee demographic data, Organization data."],
        "outputs": ["Calculated Compensation Blueprints, Revision Histories."],
        "dependencies": "Consumes Employee. Consumed by Payroll Engine.",
        "scenarios": "Annual Appraisals -> HR inputs 10% hike -> Engine archives old EmployeeSalary -> Mints new EmployeeSalary Revision -> Payroll seamlessly uses new effective-dated salary."
    },
    {
        "filename": "04_Salary_Rule_Business_Guide",
        "title": "Salary Rule Engine",
        "purpose": "Evaluates complex string-based mathematical formulas securely.",
        "solves": "Allows HR to write rules like 'IF(Basic > 10000, 200, 0)' in the UI without causing database injection vulnerabilities.",
        "why_not_others": "Decoupling this means the Salary Engine just holds data, while this engine exclusively solves Directed Acyclic Graphs (circular dependencies).",
        "owners": ["System (Internal evaluations)", "Admin (Formula creation)"],
        "modules": ["DependencyGraph", "AST Evaluator"],
        "rules": ["Circular references (A depends on B, B depends on A) instantly throw errors.", "Only whitelisted functions (Min, Max, Round) are permitted."],
        "decisions": ["Execution order of salary components.", "The final computed numerical value of a formula."],
        "never": ["Never stores employee data.", "Never touches the database directly."],
        "inputs": ["Raw string formulas, Context variables (CTC)."],
        "outputs": ["Ordered execution list, Computed floats."],
        "dependencies": "A stateless utility consumed heavily by the Salary Engine.",
        "scenarios": "HR sets HRA = 50% Basic -> System checks if Basic depends on HRA -> No circular dependency -> Calculates Basic first -> Calculates HRA."
    },
    {
        "filename": "05_Attendance_Policy_Business_Guide",
        "title": "Attendance Policy Engine",
        "purpose": "Stores the configuration metadata for how attendance should be judged.",
        "solves": "Removes hardcoded '9 AM to 5 PM' rules. Allows HR to configure multiple shifting policies across different branches.",
        "why_not_others": "Decoupled so that calculating a punch (Attendance Engine) is separated from defining what a late punch is (Policy Engine).",
        "owners": ["HR (Configuration)", "System (Lookup)"],
        "modules": ["LatePenaltyRule", "ShiftAttendancePolicy"],
        "rules": ["Policies must be immutable; changes create new versions.", "Grace minutes do not automatically excuse late coming unless requested."],
        "decisions": ["Defines the boundaries of Late, Grace, and Overflows."],
        "never": ["Never calculates a punch.", "Never modifies employee balances.", "Never deducts leave."],
        "inputs": ["Admin configurations."],
        "outputs": ["Versioned Policy Snapshots."],
        "dependencies": "Consumes Organization. Produces for Permission and Attendance Engines.",
        "scenarios": "HR changes Late Penalty from '3 lates' to '4 lates' -> Engine versions the policy to v2 -> Future calculations use v2, historical calculations retain v1 logic."
    },
    {
        "filename": "06_Permission_Business_Guide",
        "title": "Permission Engine",
        "purpose": "Manages workflows and balances for exception requests (Early Going, Late Coming, Grace).",
        "solves": "Provides a formal request channel when an employee violates a shift policy but has a valid reason.",
        "why_not_others": "Leaves handle full days. Permissions handle minutes/hours. Mixing them corrupts the leave ledger.",
        "owners": ["Employee (Requests)", "Manager (Approvals)", "HR (Overrides)"],
        "modules": ["PermissionRequest", "PermissionBalance", "GraceRequest"],
        "rules": ["Monthly allocated limits cannot be exceeded natively.", "Overflow triggers penalty ledgers.", "Manager approval is strictly required."],
        "decisions": ["Is this request within balance?", "Should this punch be excused?"],
        "never": ["Never edits the ESSL punch.", "Never alters the base policy."],
        "inputs": ["Employee justifications, Policy Limits."],
        "outputs": ["Approved Exceptions, Updated Balances."],
        "dependencies": "Consumes Attendance Policy. Produces for Attendance Calculation.",
        "scenarios": "Employee punches at 10:10 (Policy is 10:00) -> Triggers Grace Request -> Manager approves -> Permission Engine updates balance -> Sends 'Approved' event to Attendance."
    },
    {
        "filename": "07_Attendance_Business_Guide",
        "title": "Attendance Engine",
        "purpose": "The final stateless calculator that determines daily attendance status.",
        "solves": "Cross-references raw ESSL punches against active Policies and approved Permissions to yield a final Present/Absent/Late status.",
        "why_not_others": "It is the brain of the Attendance Suite. It aggregates data rather than storing configurations.",
        "owners": ["System (Automated Calculation)", "HR (Overrides/Recalculation)"],
        "modules": ["DailyAttendance", "AttendanceReplayQueue", "LeaveConversionLedger", "AttendanceException"],
        "rules": ["Never overwrite a calculation; append to History.", "Output deterministic results based on the snapshot of the policy used.", "Penalties generated are pushed to LeaveConversionLedger."],
        "decisions": ["Final Status (Present/Absent/Half-Day/Late).", "Penalty derivations (e.g., 4 lates = Half Day Penalty)."],
        "never": ["Never edits Leave balances.", "Never alters Salary.", "Never creates policies."],
        "inputs": ["ESSL Punches, Approved Permissions, Shift Data, Policy Snapshots."],
        "outputs": ["DailyAttendance status, Calculation Trace, Penalty Ledgers."],
        "dependencies": "Consumes Employee, Shift, Permission, Policy. Produces for Leave and Payroll.",
        "scenarios": "System processes ESSL punch (10:15) -> Looks up Policy (10:00 start, 10 min grace) -> Punched past grace -> Checks Permission (None) -> Flags as Late -> Updates LateCount -> If LateCount == 4 -> Pushes Half Day Penalty to LeaveConversionLedger."
    },
    {
        "filename": "08_Leave_Policy_Business_Guide",
        "title": "Leave Policy Engine",
        "purpose": "Master configuration for leave accruals, carry forwards, and waterfall penalty conversions.",
        "solves": "Allows HR to build infinite custom leave types (Sick, Casual, Comp-Off) and determine exactly how penalties deduct from them.",
        "why_not_others": "Keeps configuration separate from the active ledger, ensuring policy updates don't accidentally wipe out employee balances.",
        "owners": ["HR (Configuration)", "System (Simulation)"],
        "modules": ["LeaveType", "LeaveAccrualRule", "LeaveCarryForwardRule", "LeaveConversionPolicy"],
        "rules": ["All changes are strictly versioned.", "Penalty mapping is a cascading array (Check CL, then EL, then LWP)."],
        "decisions": ["Eligibility for leave.", "How a penalty should be mapped to a balance."],
        "never": ["Never edits an employee's ledger.", "Never approves a leave request."],
        "inputs": ["HR Configurations."],
        "outputs": ["Versioned Rules, Penalty Waterfall Logic."],
        "dependencies": "Consumes Attendance. Produces for Leave Engine.",
        "scenarios": "HR configures 'Late Penalty' to deduct from Casual Leave first, then Earned Leave. Simulation Engine verifies math. Policy is activated."
    },
    {
        "filename": "09_Leave_Business_Guide",
        "title": "Leave Engine",
        "purpose": "Manages employee time-off requests and maintains the immutable double-entry Leave Ledger.",
        "solves": "Guarantees that a leave balance is mathematically provable by summing all credits and debits in a ledger, preventing untraceable balance corruption.",
        "why_not_others": "Leave logic is highly complex (Sandwich rules, overlapping attendance conflicts). Isolating it ensures Payroll receives clean data.",
        "owners": ["Employee (Applies leave)", "Manager (Approvals)", "System (Penalty deducts)"],
        "modules": ["LeaveLedger", "LeaveBalance", "LeaveApplication", "AttendancePenaltyLedgerProcessing"],
        "rules": ["Balances are NEVER overwritten. All changes insert a new Ledger row (+/-).", "Attendance penalties are automatically consumed based on Policy priority.", "Reservations lock balances for future dates."],
        "decisions": ["Is there sufficient balance?", "Does this conflict with a Holiday/Attendance punch?"],
        "never": ["Never modifies attendance punches.", "Never modifies salary directly."],
        "inputs": ["Leave Applications, AttendancePenaltyLedger, Leave Policies."],
        "outputs": ["Approved Leave, Updated Ledgers, LOP (Loss of Pay) flags."],
        "dependencies": "Consumes Leave Policy, Attendance, Employee. Produces for Payroll.",
        "scenarios": "Attendance Engine generates a 'Half Day Penalty' for 4 lates -> Leave Engine picks it up -> Consults Leave Policy Waterfall (CL -> EL) -> Finds sufficient CL -> Writes '-0.5 CL' to LeaveLedger -> Marks Penalty Processed."
    }
]

def generate_business_doc(engine):
    doc = f"""# {engine['title']} - Functional Business Guide

## SECTION 1: ENGINE INTRODUCTION
**What is this engine?**
The {engine['title']} is an isolated, highly cohesive domain responsible for {engine['purpose'].lower()}

**Why does this engine exist?**
{engine['solves']}

**Why can't another engine perform this work?**
{engine['why_not_others']}

## SECTION 2: BUSINESS PURPOSE
**Value Proposition:** 
By separating this logic, HR teams can manage {engine['title'].replace('Engine', '').strip()} independently without risking data corruption in other modules. It strictly enforces business rules at the configuration level rather than the code level.

## SECTION 3: BUSINESS OWNERS
The primary actors interacting with this engine are:
{chr(10).join([f"- **{role}**" for role in engine['owners']])}

## SECTION 4: MODULES INSIDE THE ENGINE
**Core Modules:**
{chr(10).join([f"- **{m}**" for m in engine['modules']])}

## SECTION 5: BUSINESS RULES
*The strict constraints this engine owns and enforces:*
{chr(10).join([f"- {r}" for r in engine['rules']])}

## SECTION 6: BUSINESS WORKFLOW
**Standard Operational Flow:**
Request Initialization -> JWT/Role Verification -> Cross-Engine Data Fetch (if required) -> Pre-Flight Policy Evaluation -> Database Transaction Execution -> Immutable Ledger/History Generation -> Async Event Broadcast.

## SECTION 7: BUSINESS DECISIONS
*What autonomous decisions this engine makes on behalf of HR:*
{chr(10).join([f"- {d}" for d in engine['decisions']])}

## SECTION 8: WHAT THIS ENGINE NEVER DOES
> [!WARNING]
> Architectural boundaries are absolute.
{chr(10).join([f"- **{n}**" for n in engine['never']])}

## SECTION 9: ENGINE INPUTS
- {', '.join(engine['inputs'])}

## SECTION 10: ENGINE OUTPUTS
- {', '.join(engine['outputs'])}

## SECTION 11: DEPENDENCIES
**Cross-Engine Mapping:**
- {engine['dependencies']}

## SECTION 12: REAL BUSINESS SCENARIOS
**Example Workflow:**
{engine['scenarios']}

## SECTION 13: CONFIGURATION GUIDE
HR/Admin can heavily configure this engine via the `/api/v2/` REST interfaces. Hardcoding is strictly forbidden; all thresholds (limits, dates, hierarchies) are dynamically evaluated at runtime.

## SECTION 14: ENGINE LIMITATIONS
This engine intentionally limits its scope to {engine['title'].replace('Engine', '').strip()} tracking. It defers all peripheral responsibilities (e.g., final monetary deduction) to the upcoming Payroll engine.

## SECTION 15: ENGINE LIFECYCLE
Initialization -> Policy Binding -> Transaction Accumulation -> Closing/Locking -> Read-Only Archival.

## SECTION 16: MODULE RELATIONSHIP DIAGRAM
```text
[Input Sources] --> [Validator Engine] --> [Policy Metadata Engine] --> [{engine['title']}] --> [Ledger / Output] --> [Consumers]
```

## SECTION 17: FUTURE EXTENSIONS
Fully primed to feed data into the upcoming **Payroll Engine**, **Analytics Engines**, and potential **Expense/Reimbursement Engines**.

## SECTION 18: FINAL BUSINESS SUMMARY
The {engine['title']} successfully isolates {engine['purpose'].lower()} It protects downstream consumers by ensuring {engine['outputs'][0]} is always mathematically and historically sound.
"""
    
    filepath = ARTIFACTS_DIR / f"{engine['filename']}.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(doc)

def generate_index():
    doc = """# HRMS Business Architecture & End-to-End Guide

## 1. Complete HRMS Architecture
The system is an **Event-Driven, Micro-Monolithic Enterprise HRMS**. Instead of tangled CRUD spaghetti, the platform is divided into rigidly isolated 'Engines'. 
- Engines communicate via stateless IDs.
- Engines *never* overwrite historical data (Immutability).
- Rules are injected via Metadata, never hardcoded.

## 2. End-to-End Employee Lifecycle
```text
1. Organization Setup (Branches, Depts mapped)
   ↓
2. Employee Onboarding (Profile creation, mapped to Org)
   ↓
3. Salary Blueprint Assigned (Formulas calculated)
   ↓
4. Leave Policies & Attendance Policies Activated
   ↓
5. Daily Punches (Attendance Engine calculates against Policy)
   ↓
6. Exceptions (Permissions & Grace invoked by Employee)
   ↓
7. Penalties (Unresolved Exceptions pushed to Leave Ledger)
   ↓
8. PAYROLL (Coming Soon: Consumes Salary + Attendance + Leave Ledgers)
```

## 3. Business Rules Ownership
- **Who owns geographical structure?** Organization Engine.
- **Who owns hierarchical approval routing?** Employee Engine.
- **Who owns what time constitutes 'Late'?** Attendance Policy Engine.
- **Who owns deducting leave for being late?** Leave Engine (via AttendancePenaltyLedgerProcessing).

## 4. Integration Points & Future Integration
Every engine exposes `/api/v2/` endpoints secured by JWT. 
The system is perfectly staged for the **Payroll Engine**, which will simply act as a mathematical synthesizer:
`Payroll = Salary Base(Salary Engine) + LOP Days(Attendance/Leave Engines) + Deductions`

## 5. Engine Documentation Links
- [Organization Engine Guide](file:///C:/Users/dell/.gemini/antigravity-ide/brain/0093acac-024f-4ad3-8651-7c86d23f77d2/01_Organization_Business_Guide.md)
- [Employee Engine Guide](file:///C:/Users/dell/.gemini/antigravity-ide/brain/0093acac-024f-4ad3-8651-7c86d23f77d2/02_Employee_Business_Guide.md)
- [Salary Engine Guide](file:///C:/Users/dell/.gemini/antigravity-ide/brain/0093acac-024f-4ad3-8651-7c86d23f77d2/03_Salary_Business_Guide.md)
- [Salary Rule Engine Guide](file:///C:/Users/dell/.gemini/antigravity-ide/brain/0093acac-024f-4ad3-8651-7c86d23f77d2/04_Salary_Rule_Business_Guide.md)
- [Attendance Policy Engine Guide](file:///C:/Users/dell/.gemini/antigravity-ide/brain/0093acac-024f-4ad3-8651-7c86d23f77d2/05_Attendance_Policy_Business_Guide.md)
- [Permission Engine Guide](file:///C:/Users/dell/.gemini/antigravity-ide/brain/0093acac-024f-4ad3-8651-7c86d23f77d2/06_Permission_Business_Guide.md)
- [Attendance Engine Guide](file:///C:/Users/dell/.gemini/antigravity-ide/brain/0093acac-024f-4ad3-8651-7c86d23f77d2/07_Attendance_Business_Guide.md)
- [Leave Policy Engine Guide](file:///C:/Users/dell/.gemini/antigravity-ide/brain/0093acac-024f-4ad3-8651-7c86d23f77d2/08_Leave_Policy_Business_Guide.md)
- [Leave Engine Guide](file:///C:/Users/dell/.gemini/antigravity-ide/brain/0093acac-024f-4ad3-8651-7c86d23f77d2/09_Leave_Business_Guide.md)
"""
    
    filepath = ARTIFACTS_DIR / "HRMS_Business_Architecture_Guide.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(doc)

if __name__ == "__main__":
    for engine in ENGINES:
        generate_business_doc(engine)
    generate_index()
    print("Business Guides generated successfully.")
