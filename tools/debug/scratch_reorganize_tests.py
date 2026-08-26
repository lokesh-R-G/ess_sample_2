import os
import shutil

backend_dir = r"C:\ess\ess_sample_2\backend"
root_dir = r"C:\ess\ess_sample_2"

test_dir = os.path.join(backend_dir, "tests")
dirs_to_create = ["unit", "integration", "regression", "audit", "fixtures", "scripts"]

for d in dirs_to_create:
    os.makedirs(os.path.join(test_dir, d), exist_ok=True)

moved_files = []

def should_move(filename):
    if not filename.endswith('.py'):
        return False
    # Only standalone scripts not inside app/ or tests/
    if filename in ['main.py', 'conftest.py']:
        return False
    return filename.startswith(('test_', 'check_', 'audit_', 'verify_'))

def process_dir(directory):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            if should_move(item):
                # determine target dir
                target_sub = "audit"
                if item.startswith('test_'):
                    target_sub = "integration"
                
                target_path = os.path.join(test_dir, target_sub, item)
                
                if not os.path.exists(target_path):
                    shutil.move(item_path, target_path)
                    moved_files.append((item_path, target_path))

# Root scripts
process_dir(backend_dir)
process_dir(root_dir)

with open(r"C:\Users\dell\.gemini\antigravity-ide\brain\6ed04bf3-0d2b-4c5c-9063-59d073c4f9d0\test_reorganization.md", "w") as f:
    f.write("# Test Reorganization\n\n")
    f.write("Moved standalone scripts to `backend/tests` structure.\n\n")
    f.write("| Original Location | New Location |\n")
    f.write("|---|---|\n")
    for src, dst in moved_files:
        f.write(f"| `{src}` | `{dst}` |\n")
