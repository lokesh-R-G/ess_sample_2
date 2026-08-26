import os
import sys

def search_files(directory, query):
    results = []
    for root, dirs, files in os.walk(directory):
        if 'node_modules' in root or '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.tsx', '.ts')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f):
                            if query.lower() in line.lower():
                                results.append(f"{path}:{i+1}: {line.strip()}")
                except:
                    pass
    return results

print("--- Trip Sheet ---")
for r in search_files(r'c:\ess\ess_sample_2', 'trip'):
    if 'trip_sheet' in r or 'tripsheet' in r.lower():
        print(r)

print("\n--- Cash Voucher ---")
for r in search_files(r'c:\ess\ess_sample_2', 'cash'):
    if 'voucher' in r.lower():
        print(r)

print("\n--- Manage Employee ---")
for r in search_files(r'c:\ess\ess_sample_2\src', 'manage'):
    print(r)
