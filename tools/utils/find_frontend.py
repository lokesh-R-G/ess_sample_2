import os
for root, _, files in os.walk('src'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            name = file.lower()
            if 'payroll' in name or 'settings' in name or 'pf' in name or 'esi' in name or 'pt' in name:
                print(os.path.join(root, file))
