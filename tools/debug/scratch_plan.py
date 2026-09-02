import os
import json
import re

def main():
    with open('routes.json') as f:
        routes = json.load(f)
        
    v1_routes = [r for r in routes if '/v1/' in r['path']]
    v2_routes = [r for r in routes if '/v2/' in r['path']]
    
    with open('C:\\Users\\dell\\.gemini\\antigravity-ide\\brain\\6ed04bf3-0d2b-4c5c-9063-59d073c4f9d0\\implementation_plan.md', 'w') as out:
        out.write("# ESS HRMS V2 - Dashboard Refactor & Codebase Audit\n\n")
        out.write("## Proposed Changes\n\n")
        out.write("This plan covers the complete V2 transition and codebase cleanup.\n\n")
        out.write("### 1. Dashboard Migration\n")
        out.write("- Current Dashboard uses V1 legacy models for Attendance and Leave.\n")
        out.write("- **Goal**: Wire the Dashboard to V2 Engine metrics, Leave Ledgers, and Employee Organization data without relying on hardcoded calculations.\n")
        out.write("\n### 2. Codebase Cleanup\n")
        out.write("- Analyze and classify all endpoints.\n")
        out.write("- Remove unused legacy V1 APIs and services.\n")
        out.write("\n### User Review Required\n")
        out.write("> [!IMPORTANT]\n> Before I start generating the detailed artifacts (API Consumption, Database Matrices), please confirm if you want me to proceed with Phase 1 and Phase 2 immediately, as the audit involves generating large diagnostic reports.")
        
if __name__ == '__main__':
    main()
