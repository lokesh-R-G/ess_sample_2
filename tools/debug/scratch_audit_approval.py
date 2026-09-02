import os
import glob

def audit_directory(path):
    print(f"--- Auditing {path} ---")
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py') or file.endswith('.ts') or file.endswith('.tsx'):
                filepath = os.path.join(root, file)
                print(f"\nFile: {filepath}")
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        print(f"Lines: {len(lines)}")
                        # Print classes, functions, and models
                        for line in lines:
                            if 'class ' in line or 'def ' in line or 'interface ' in line or 'export const' in line:
                                print("  " + line.strip())
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

if __name__ == "__main__":
    audit_directory(r"c:\ess\ess_sample_2\backend\app\approval")
    audit_directory(r"c:\ess\ess_sample_2\src\pages\approvals")
    
