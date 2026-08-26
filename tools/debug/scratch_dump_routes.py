import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath("."))

from app.main import app

def dump_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, "methods"):
            # It's an APIRoute
            for method in route.methods:
                # filter out HEAD and OPTIONS if not explicitly defined? Actually let's just keep everything
                if method not in ['HEAD', 'OPTIONS']:
                    routes.append({
                        "path": route.path,
                        "method": method,
                        "name": route.name,
                    })
    
    import json
    with open("routes.json", "w") as f:
        json.dump(routes, f, indent=2)
    print(f"Dumped {len(routes)} routes to routes.json")

if __name__ == "__main__":
    dump_routes()
