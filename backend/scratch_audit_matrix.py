import os
import glob
import ast
import json

def get_pydantic_fields(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    classes = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            fields = []
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    field_name = item.target.id
                    field_type_raw = ast.unparse(item.annotation)
                    fields.append((field_name, field_type_raw))
            classes[node.name] = fields
    return classes

def find_files_with_keyword(directory, keywords):
    matched = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                for k in keywords:
                    if k in file.lower() or k in root.lower():
                        matched.append(file_path)
                        break
    return matched

if __name__ == "__main__":
    base_dir = "c:/ess/ess_sample_2/backend/app"
    keywords = ["holiday", "branch", "employee", "employment", "shift", "attendance_policy", "weekly_off_policy", "context_resolver", "policy_engine", "attendance_processor", "attendance_snapshot", "attendance_v2"]
    
    files = find_files_with_keyword(base_dir, keywords)
    
    data = {}
    for file in files:
        if "schemas" in file or "models" in file:
            try:
                classes = get_pydantic_fields(file)
                for c_name, c_fields in classes.items():
                    data[c_name] = c_fields
            except Exception as e:
                pass

    with open("c:/ess/ess_sample_2/backend/scratch_audit_matrix.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
