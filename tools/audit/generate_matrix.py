import os
import ast
import json

base_dir = "c:/ess/ess_sample_2/backend/app"

MODELS_TO_CHECK = {
    "HolidayCalendar": "holiday_calendar/schemas",
    "Holiday": "holiday_calendar/schemas",
    "Branch": "organization/schemas",
    "Employee": "employee/schemas",
    "Employment": "employee/schemas",
    "Shift": "organization/schemas",
    "ShiftDefinition": "shift/schemas",
    "AttendancePolicy": "attendance_policy/schemas",
    "WeeklyOffPolicy": "attendance_policy/schemas",
    "ShiftAssignment": "employee/schemas",
    "AttendanceSnapshot": "attendance_v2/schemas"
}

def get_pydantic_fields(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)
    classes = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            fields = {}
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    fname = item.target.id
                    ftype = ast.unparse(item.annotation)
                    fields[fname] = ftype
            classes[node.name] = fields
    return classes

def check_standard_fields(fields):
    standard = ["code", "version", "effectiveFrom", "effectiveTo", "isCurrent", "status", "createdAt", "updatedAt"]
    found = {s: (s in fields) for s in standard}
    return found

def find_relations(fields):
    obj_ids = []
    codes = []
    for fname, ftype in fields.items():
        if "id" in fname.lower() and "str" in ftype.lower():
            obj_ids.append(fname)
        if "code" in fname.lower() and "str" in ftype.lower():
            codes.append(fname)
    return obj_ids, codes

def run_analysis():
    all_classes = {}
    # Scan for classes
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    all_classes.update(get_pydantic_fields(path))
                except:
                    pass

    md = ["# ESS HRMS Dependency Matrix Audit\n"]
    md.append("## 1. Entity Field Analysis\n")
    
    # We want to check the specific models
    # Wait, the class names might have "Model" suffix like "BranchModel"
    target_names = [
        "HolidayCalendarModel", "HolidayModel", "BranchModel", "EmployeeModel", 
        "EmploymentModel", "ShiftModel", "ShiftDefinitionModel", 
        "AttendancePolicyModel", "WeeklyOffPolicyModel", "ShiftAssignmentModel", 
        "AttendanceSnapshotModel", "AttendanceRecordModel",
        "HolidayCalendar", "Holiday", "Branch", "Employee", "Employment",
        "Shift", "ShiftDefinition", "AttendancePolicy", "WeeklyOffPolicy",
        "ShiftAssignment", "AttendanceSnapshot"
    ]
    
    md.append("| Entity | ObjectId Relationships | Code Relationships | Missing Standard Fields |")
    md.append("|---|---|---|---|")
    
    for t in target_names:
        if t in all_classes:
            fields = all_classes[t]
            std = check_standard_fields(fields)
            missing = [k for k, v in std.items() if not v]
            obj_ids, codes = find_relations(fields)
            
            missing_str = ", ".join(missing) if missing else "None"
            obj_ids_str = ", ".join(obj_ids) if obj_ids else "None"
            codes_str = ", ".join(codes) if codes else "None"
            
            md.append(f"| {t} | {obj_ids_str} | {codes_str} | {missing_str} |")
            
    md.append("\n## 2. Runtime Resolution Path Analysis")
    md.append("\n### Employee -> Branch -> Holiday Calendar")
    md.append("1. Employee has `branchId` (ObjectId) or `companyId`.")
    md.append("2. ContextResolver uses `branchId` to find Branch.")
    md.append("3. ContextResolver or PolicyEngine finds HolidayCalendar where `branchId` matches.")
    
    md.append("\n### Employee -> Shift -> Attendance Policy / Weekly Off Policy -> Context Resolver -> Policy Engine")
    md.append("1. `AttendanceProcessor` loads `Employee` and `Employment`.")
    md.append("2. `AttendanceContextResolver` resolves the active `Shift`, `AttendancePolicy`, and `WeeklyOffPolicy` for the given date using either direct `shiftId` / `attendancePolicyId` on Employee/Employment or via assignments.")
    md.append("3. `PolicyEngine` consumes these resolved policies (passed as dictionaries/models).")
    md.append("4. Output is an `AttendanceSnapshot` (or `AttendanceRecord`) written to DB.")

    md.append("\n## 3. Impact of Replacing ObjectIds with Business Codes")
    md.append("If `ObjectId` foreign keys (like `employeeId`, `branchId`, `shiftId`, `policyId`) are replaced by immutable `code` + `version` combinations:")
    md.append("- **Collections to Update:** Every single mapping collection (e.g., `ShiftAssignment`, `Employment`, `AttendanceRecord`) must store the `code` and `version` rather than `ObjectId`.")
    md.append("- **Context Resolver:** Must query by `{code: ..., version: ...}` instead of `_id`.")
    md.append("- **Historical Integrity:** A snapshot referencing `shiftCode='MORNING', version=2` natively preserves the exact policy rules active at that time.")
    
    with open("c:/ess/ess_sample_2/backend/dependency_matrix_audit.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))

if __name__ == "__main__":
    run_analysis()
