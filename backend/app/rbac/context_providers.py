from fastapi import HTTPException, Request
from app.rbac.engine import _get_db
from typing import Dict

async def employee_context_provider(emp_id: str) -> Dict[str, str]:
    """Resolve an employee resource for RBAC scope checks.
    Returns a dict with canonical identifiers required by the engine:
    - empId (canonical employeeId)
    - branchId
    - companyId
    - managerId (optional, used by TEAM scope)
    """
    db = _get_db()
    employee = await db.employees.find_one({"employeeId": emp_id})
    print("EMPLOYEE_CONTEXT_PROVIDER:", emp_id, employee)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    # Ensure ObjectId fields are stringified for JSON serialisation if present
    return {
        "empId": employee.get("employeeId"),
        "branchId": employee.get("branchId"),
        "companyId": employee.get("companyId"),
        "managerId": employee.get("managerId"),
    }

def resource_context_provider(provider_callable: callable):
    """Wrap a provider for use with ``require_permission``.
    The wrapper matches FastAPI's ``Depends`` call signature – it receives
    any path/query parameters needed by ``provider_callable`` and returns the
    context dict expected by the RBAC engine.
    """
    async def wrapper(**kwargs):
        return await provider_callable(**kwargs)
    return wrapper

from fastapi import Request

def self_context(user: dict) -> dict:
    return {"empId": user.get("employeeId")}

async def employee_context_by_emp_id(request: Request, **kwargs) -> dict:
    emp_id = request.path_params.get("emp_id")
    if not emp_id:
        raise HTTPException(status_code=404, detail="Employee ID missing in path")
    return await employee_context_provider(emp_id)
