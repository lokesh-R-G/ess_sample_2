from typing import Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone

async def get_authoritative_employee_name(db: AsyncIOMotorDatabase, employee_id: Optional[str] = None, employee_code: Optional[str] = None) -> Tuple[Optional[str], Optional[dict]]:
    """
    Retrieves the authoritative name for an employee.
    Priority:
    1. Active employee_personals record matching employeeId.
    2. Fallback to employee collection record matching employeeId or employeeCode.
    Returns: (full_name, employee_doc)
    """
    emp = None
    if employee_id:
        emp = await db.employees.find_one({"employeeId": str(employee_id), "deletedAt": None})
        if not emp:
            emp = await db.employees.find_one({"employeeId": str(employee_id)})
    if not emp and employee_code:
        emp = await db.employees.find_one({"employeeCode": str(employee_code), "deletedAt": None})
        if not emp:
            emp = await db.employees.find_one({"employeeCode": str(employee_code)})
        if not emp:
            emp = await db.employees.find_one({"employeeId": str(employee_code)})

    # Also resolve employeeId from emp if we only had employeeCode
    resolved_emp_id = emp.get("employeeId") if emp else employee_id

    personal_name = None
    if resolved_emp_id:
        personal = await db.employee_personals.find_one({"employeeId": str(resolved_emp_id), "isCurrent": True, "deletedAt": None})
        if not personal:
            personal = await db.employee_personals.find_one({"employeeId": str(resolved_emp_id), "isCurrent": True})
        if not personal:
            personal = await db.employee_personals.find_one({"employeeId": str(resolved_emp_id)})
            
        if personal:
            first = (personal.get("firstName") or "").strip()
            last = (personal.get("lastName") or "").strip()
            full = f"{first} {last}".strip()
            if full:
                personal_name = full

    if personal_name:
        return personal_name, emp

    if emp:
        first = (emp.get("firstName") or "").strip()
        last = (emp.get("lastName") or "").strip()
        full = f"{first} {last}".strip()
        if full:
            return full, emp

    return None, emp


async def sync_user_name_from_employee(db: AsyncIOMotorDatabase, employee_id: Optional[str] = None, employee_code: Optional[str] = None) -> Optional[str]:
    """
    Synchronizes the authoritative employee name to the corresponding user record in `users`.
    """
    name, emp = await get_authoritative_employee_name(db, employee_id, employee_code)
    if not name:
        return None

    user_query = {}
    emp_code = emp.get("employeeCode") if emp else employee_code
    emp_id = emp.get("employeeId") if emp else employee_id

    # Construct safe query to match user
    or_clauses = []
    if emp_id:
        or_clauses.append({"employeeId": str(emp_id)})
    if emp_code:
        or_clauses.append({"employeeCode": str(emp_code)})
        or_clauses.append({"empId": str(emp_code)})
        or_clauses.append({"username": str(emp_code)})

    if not or_clauses:
        return None

    user_query = {"$or": or_clauses}
    now = datetime.now(timezone.utc)
    
    # Update all matching user documents for this employee (typically exactly 1)
    await db.users.update_many(
        user_query,
        {
            "$set": {
                "name": name,
                "updatedAt": now
            }
        }
    )
    return name

