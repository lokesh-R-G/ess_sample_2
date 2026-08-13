import os
import re
import json

def find_frontend_api_calls(src_dir):
    api_calls = []
    # match patterns like api.get('/v1/attendance/...
    # or fetch(`/api/v2/...
    regex = re.compile(r"api\.(get|post|put|delete|patch|options)<[^>]*>\s*\(\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
    regex2 = re.compile(r"api\.(get|post|put|delete|patch|options)\s*\(\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
    
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Match first pattern
                        for match in regex.finditer(content):
                            method = match.group(1).upper()
                            endpoint = match.group(2)
                            api_calls.append({
                                'file': path.replace(src_dir, '').lstrip('\\/'),
                                'method': method,
                                'endpoint': endpoint
                            })
                            
                        # Match second pattern
                        for match in regex2.finditer(content):
                            method = match.group(1).upper()
                            endpoint = match.group(2)
                            api_calls.append({
                                'file': path.replace(src_dir, '').lstrip('\\/'),
                                'method': method,
                                'endpoint': endpoint
                            })
                except Exception as e:
                    print(f"Error parsing {path}: {e}")
                    
    return api_calls

if __name__ == '__main__':
    frontend_dir = r"C:\ess\ess_sample_2\src"
    api_calls = find_frontend_api_calls(frontend_dir)
    
    # Remove duplicates from overlapping regexes
    unique_calls = []
    seen = set()
    for call in api_calls:
        key = (call['file'], call['method'], call['endpoint'])
        if key not in seen:
            seen.add(key)
            unique_calls.append(call)
            
    with open("frontend_api_calls.json", "w") as f:
        json.dump(unique_calls, f, indent=2)
    print(f"Dumped {len(unique_calls)} unique frontend API calls to frontend_api_calls.json")
