import os
import ast

def find_payroll_files():
    keywords = ['payroll', 'salary', 'payslip', 'statutory', 'pf', 'esi', 'pt', 'attendance', 'leave', 'permission']
    target_classes = ['PayrollCalculationEngine', 'SalaryCalculationEngine', 'SalaryAssignmentService', 'EmployeeSalaryComponent', 'PayrollCycle', 'Payroll', 'PayrollLineItem', 'Payslip', 'AttendanceProcessor', 'PolicyEngine', 'LeaveLedgerService', 'PermissionLedgerService']
    
    results = {
        "files_with_keywords_in_name": [],
        "files_with_target_classes": {}
    }
    
    for root, _, files in os.walk('.'):
        if 'venv' in root or '.git' in root or '__pycache__' in root:
            continue
            
        for file in files:
            if not file.endswith('.py'):
                continue
                
            path = os.path.join(root, file)
            
            # Check file name
            if any(kw in file.lower() for kw in keywords):
                results["files_with_keywords_in_name"].append(path)
                
            # Parse AST to find target classes
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if node.name in target_classes:
                            if path not in results["files_with_target_classes"]:
                                results["files_with_target_classes"][path] = []
                            results["files_with_target_classes"][path].append(node.name)
            except:
                pass
                
    return results

if __name__ == "__main__":
    import pprint
    res = find_payroll_files()
    pprint.pprint(res)
