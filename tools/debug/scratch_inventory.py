import os
import ast

def analyze_fastapi_routes(base_dir):
    routes = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                for dec in node.decorator_list:
                                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                                        if dec.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                            router_name = ''
                                            if isinstance(dec.func.value, ast.Name):
                                                router_name = dec.func.value.id
                                            route_path = ''
                                            if dec.args and isinstance(dec.args[0], ast.Constant):
                                                route_path = dec.args[0].value
                                            routes.append({
                                                'file': path,
                                                'method': dec.func.attr.upper(),
                                                'path': route_path,
                                                'router': router_name,
                                                'function': node.name
                                            })
                except Exception as e:
                    print(f"Error parsing {path}: {e}")
    return routes

if __name__ == '__main__':
    backend_dir = r"C:\ess\ess_sample_2\backend"
    routes = analyze_fastapi_routes(backend_dir)
    print(f"Found {len(routes)} API routes")
    for r in routes:
        if 'v1' in r['file'] or 'v1' in r['path']:
            print(f"V1 Route: {r['method']} {r['path']} in {r['file']}")
        elif 'v2' in r['file'] or 'v2' in r['path']:
            print(f"V2 Route: {r['method']} {r['path']} in {r['file']}")
