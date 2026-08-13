import os
import re

search_paths = [
    r"c:\ess\ess_sample_2\backend\app",
    r"c:\ess\ess_sample_2\src",
]

terms = [
    "/api/v1/dashboard",
    "dashboardService",
    "dashboard.py",
    "get_attendance_for_employee"
]

results = []

for root, dirs, files in os.walk(r"c:\ess\ess_sample_2"):
    if 'node_modules' in root or '.git' in root or '__pycache__' in root or 'dist' in root or '.pytest_cache' in root:
        continue
    for file in files:
        if not file.endswith(('.ts', '.tsx', '.py', '.js', '.jsx')):
            continue
            
        filepath = os.path.join(root, file)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for term in terms:
                if term in content:
                    results.append((term, filepath))
        except:
            pass

from collections import defaultdict
grouped = defaultdict(list)
for term, filepath in results:
    grouped[term].append(filepath)
    
with open(r"C:\Users\dell\.gemini\antigravity-ide\brain\6ed04bf3-0d2b-4c5c-9063-59d073c4f9d0\dashboard_audit_results.md", "w", encoding='utf-8') as f:
    f.write("# Dashboard V1 Audit Results\n\n")
    for term, paths in grouped.items():
        f.write(f"### Term: `{term}`\n")
        for p in set(paths):
            f.write(f"- `{p}`\n")
        f.write("\n")
