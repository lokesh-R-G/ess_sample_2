import os
import re

def grep(directory, pattern):
    results = []
    for root, _, files in os.walk(directory):
        if 'venv' in root or '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            if not (file.endswith('.py') or file.endswith('.ts') or file.endswith('.tsx')):
                continue
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        if re.search(pattern, line, re.IGNORECASE):
                            results.append(f"{path}:{i+1} {line.strip()}")
            except:
                pass
    return results

print("=== BANK EXPORT ===")
for r in grep('c:\\ess\\ess_sample_2', 'bank export|csv|export'):
    print(r)

print("=== PAYSLIP ===")
for r in grep('c:\\ess\\ess_sample_2', 'payslip'):
    print(r)
    
