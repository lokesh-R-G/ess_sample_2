import json
import re

def generate_api_consumption_matrix():
    with open('routes.json') as f:
        routes = json.load(f)
        
    with open('frontend_api_calls.json') as f:
        frontend_calls = json.load(f)
        
    matrix_md = "# API Consumption Matrix\n\n"
    matrix_md += "| Method | Endpoint | V1/V2 | Frontend Consumer | Used? |\n"
    matrix_md += "|---|---|---|---|---|\n"
    
    # Simple regex matching for endpoints (removing path params)
    def normalize_path(path):
        # convert /{id} or /{emp_id} to /{}
        return re.sub(r'\{[^}]+\}', '{}', path).rstrip('/')
        
    frontend_patterns = []
    for fc in frontend_calls:
        frontend_patterns.append({
            "method": fc['method'],
            # The frontend calls use string templates sometimes like `/v1/attendance/${empId}` 
            # We'll just extract the base path for matching
            "base_endpoint": fc['endpoint'].split('${')[0].rstrip('/'),
            "file": fc['file']
        })
        
    unused_v1 = []
    
    for r in routes:
        method = r['method']
        path = r['path']
        is_v2 = '/v2/' in path
        version = 'V2' if is_v2 else 'V1'
        
        base_path = normalize_path(path)
        
        consumers = []
        for fp in frontend_patterns:
            # If the backend route base matches the frontend base route
            # Example: backend `/api/v1/attendance/{emp_id}/` vs frontend `/v1/attendance/`
            # Frontend doesn't always have `/api/` prefix in the call (axios base URL usually has it)
            if fp['method'] == method and fp['base_endpoint'] in path:
                consumers.append(fp['file'])
                
        consumers = list(set(consumers))
        used = 'Yes' if len(consumers) > 0 else 'No'
        
        if not is_v2 and not used:
            unused_v1.append(r)
            
        consumer_str = "<br>".join(consumers) if consumers else "None"
        matrix_md += f"| {method} | {path} | {version} | {consumer_str} | {used} |\n"
        
    with open(r"C:\Users\dell\.gemini\antigravity-ide\brain\6ed04bf3-0d2b-4c5c-9063-59d073c4f9d0\api_consumption_matrix.md", "w") as f:
        f.write(matrix_md)
        
    removal_md = "# V1 Removal Candidates\n\n"
    removal_md += "The following V1 endpoints have no frontend consumers and are candidates for safe removal.\n\n"
    for r in unused_v1:
        removal_md += f"- `{r['method']} {r['path']}`\n"
        
    with open(r"C:\Users\dell\.gemini\antigravity-ide\brain\6ed04bf3-0d2b-4c5c-9063-59d073c4f9d0\v1_removal_candidates.md", "w") as f:
        f.write(removal_md)

if __name__ == '__main__':
    generate_api_consumption_matrix()
