import os
import ast

def audit_routes(app_dir):
    findings = []
    for root, _, files in os.walk(app_dir):
        for file in files:
            if file.endswith('.py') and ('route' in file or file == 'router.py'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            is_route = False
                            for dec in node.decorator_list:
                                if isinstance(dec, ast.Call):
                                    if hasattr(dec.func, 'attr') and dec.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                        is_route = True
                            
                            if is_route:
                                has_user = False
                                has_perm = False
                                for arg in node.args.args + node.args.kwonlyargs:
                                    if arg.annotation:
                                        # Very basic check
                                        arg_str = ast.unparse(arg)
                                        if 'get_current_user' in arg_str:
                                            has_user = True
                                        if 'require_permission' in arg_str or 'require_roles' in arg_str:
                                            has_perm = True
                                            
                                if not has_user or not has_perm:
                                    rel_path = os.path.relpath(path, app_dir)
                                    findings.append({
                                        'file': rel_path,
                                        'function': node.name,
                                        'has_user': has_user,
                                        'has_perm': has_perm
                                    })
                except Exception as e:
                    pass
    return findings

if __name__ == '__main__':
    app_dir = r'c:\ess\ess_sample_2\backend\app'
    findings = audit_routes(app_dir)
    for f in findings:
        print(f"{f['file']} - {f['function']}: UserAuth={f['has_user']}, PermAuth={f['has_perm']}")
