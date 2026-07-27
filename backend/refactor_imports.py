import os
import re

app_dir = r"c:\ess\ess_sample_2\backend\app"

def get_module_parts(file_path):
    rel_path = os.path.relpath(file_path, r"c:\ess\ess_sample_2\backend")
    parts = os.path.normpath(rel_path).replace('.py', '').split(os.sep)
    if parts[-1] == '__init__':
        parts = parts[:-1]
    return parts

def resolve_import(module_parts, dots, import_path):
    level = len(dots)
    base = module_parts[:-level] if level > 0 else module_parts
    
    parts = base
    if import_path:
        parts = parts + import_path.split('.')
        
    if len(parts) > 0 and parts[0] != 'app':
        parts.insert(0, 'app')
        
    return ".".join(parts)

def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        module_parts = get_module_parts(file_path)
        
        def replacer(match):
            dots = match.group(1)
            import_path = match.group(2)
            resolved = resolve_import(module_parts, dots, import_path)
            if resolved:
                return f"from {resolved} import"
            return match.group(0)

        # Match "from ...something import"
        new_content = re.sub(r"^from\s+(\.+)([\w\.]*)\s+import", replacer, content, flags=re.MULTILINE)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    count = 0
    for root, _, files in os.walk(app_dir):
        for f in files:
            if f.endswith('.py'):
                process_file(os.path.join(root, f))
                count += 1
    print(f"Processed {count} files.")
