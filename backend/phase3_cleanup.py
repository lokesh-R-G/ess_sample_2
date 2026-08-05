import os
from pathlib import Path

backend_dir = Path("c:/ess/ess_sample_2/backend")

files_to_delete = [
    # Grace Policy
    "app/attendance_policy/models/grace_policy.py",
    "app/attendance_policy/schemas/grace_policy.py",
    "app/attendance_policy/validators/grace_policy_validator.py",
    "app/attendance_policy/repositories/grace_policy_repository.py",
    "app/attendance_policy/services/grace_policy_service.py",
    "app/attendance_policy/controllers/grace_policy_controller.py",
    "app/attendance_policy/routes/grace_policy_routes.py",
    # Late Policy
    "app/attendance_policy/models/late_policy.py",
    "app/attendance_policy/schemas/late_policy.py",
    "app/attendance_policy/validators/late_policy_validator.py",
    "app/attendance_policy/repositories/late_policy_repository.py",
    "app/attendance_policy/services/late_policy_service.py",
    "app/attendance_policy/controllers/late_policy_controller.py",
    "app/attendance_policy/routes/late_policy_routes.py",
]

for f in files_to_delete:
    file_path = backend_dir / f
    if file_path.exists():
        os.remove(file_path)
        print(f"Deleted: {f}")
    else:
        print(f"Not found: {f}")

# Update generate_docs.py
docs_file = backend_dir / "app/scripts/generate_docs.py"
if docs_file.exists():
    content = docs_file.read_text()
    # Remove GracePolicy, LatePolicy from the list
    content = content.replace('"GracePolicy", ', '').replace('"LatePolicy", ', '')
    docs_file.write_text(content)
    print("Updated generate_docs.py")

# Update generate_business_docs.py
b_docs_file = backend_dir / "app/scripts/generate_business_docs.py"
if b_docs_file.exists():
    content = b_docs_file.read_text()
    content = content.replace('"GracePolicy", ', '').replace('"LatePolicy", ', '')
    b_docs_file.write_text(content)
    print("Updated generate_business_docs.py")

print("Cleanup complete.")
