import os
from pathlib import Path

FOLDERS = ["controllers", "services", "repositories", "schemas", "models", "validators", "dtos", "routes", "events", "constants", "exceptions", "interfaces", "types", "utils", "tests"]

def create_structure(base_path, modules):
    for module in modules:
        mod_path = base_path / module
        mod_path.mkdir(parents=True, exist_ok=True)
        (mod_path / "__init__.py").touch()
        for folder in FOLDERS:
            folder_path = mod_path / folder
            folder_path.mkdir(exist_ok=True)
            (folder_path / "__init__.py").touch()

def write_ess(base_path):
    mod = base_path / "ess"
    route = """from fastapi import APIRouter
router = APIRouter(prefix="/ess", tags=["Employee Self Service Engine"])

@router.get("/dashboard")
async def ess_dashboard():
    return {"status": "Success", "message": "ESS Dashboard data aggregated."}

@router.get("/payslips")
async def ess_payslips():
    return {"status": "Success", "message": "ESS Payslips fetched from Payslip Engine."}
"""
    with open(mod / "routes" / "router.py", "w") as f:
        f.write(route)

def write_mss(base_path):
    mod = base_path / "mss"
    route = """from fastapi import APIRouter
router = APIRouter(prefix="/mss", tags=["Manager Self Service Engine"])

@router.get("/dashboard")
async def mss_dashboard():
    return {"status": "Success", "message": "MSS Dashboard aggregated."}

@router.get("/approvals")
async def mss_approvals():
    return {"status": "Success", "message": "Pending approvals fetched via Workflow Engine."}
"""
    with open(mod / "routes" / "router.py", "w") as f:
        f.write(route)

def write_organization_policy(base_path):
    mod = base_path / "organization_policy"
    route = """from fastapi import APIRouter
router = APIRouter(prefix="/organization-policy", tags=["Organization Policy Engine"])

@router.post("/create")
async def create_org_policy():
    return {"status": "Success", "message": "Organization Policy drafted."}

@router.post("/publish")
async def publish_org_policy():
    return {"status": "Success", "message": "Organization Policy published. Immutable version created."}
"""
    with open(mod / "routes" / "router.py", "w") as f:
        f.write(route)

def write_calendar(base_path):
    mod = base_path / "calendar"
    route = """from fastapi import APIRouter
router = APIRouter(prefix="/calendar", tags=["Calendar Engine"])

@router.get("/company")
async def get_company_calendar():
    return {"status": "Success", "message": "Shared company calendar populated from Holiday & Leave engines."}
"""
    with open(mod / "routes" / "router.py", "w") as f:
        f.write(route)

if __name__ == "__main__":
    base = Path(r"c:\ess\ess_sample_2\backend\app")
    modules = ["ess", "mss", "organization_policy", "calendar"]
    create_structure(base, modules)
    write_ess(base)
    write_mss(base)
    write_organization_policy(base)
    write_calendar(base)
    print("Part 2 Engines Generated.")
