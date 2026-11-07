from typing import List, Optional, Set
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

async def get_manager_identifiers(db: AsyncIOMotorDatabase, manager_employee_id: str) -> List[str]:
    """
    Finds all identifiers used in the system for this manager.
    In the system:
    - employeeId (e.g. '1', '6', '7')
    - _id as str (e.g. '6a9169127ab63c8399399515', '6ac7365254ca7cb7903557d5')
    - employeeCode (e.g. '5188', '423001')
    """
    identifiers = set()
    manager_str = str(manager_employee_id).strip()
    identifiers.add(manager_str)

    # Find all employee records that could represent this manager:
    # 1. Matching employeeId (active preferred)
    # 2. Matching employeeCode
    # 3. Matching _id if 24-char hex
    or_clauses = [{"employeeId": manager_str}, {"employeeCode": manager_str}]
    if len(manager_str) == 24:
        try:
            or_clauses.append({"_id": ObjectId(manager_str)})
        except Exception:
            pass

    cursor = db.employees.find({"$or": or_clauses})
    async for emp in cursor:
        if emp.get("_id"):
            identifiers.add(str(emp["_id"]))
        if emp.get("employeeId"):
            identifiers.add(str(emp["employeeId"]))
        if emp.get("employeeCode"):
            identifiers.add(str(emp["employeeCode"]))

    return list(identifiers)


async def get_reporting_employee_ids(db: AsyncIOMotorDatabase, manager_employee_id: str, include_self: bool = False) -> List[str]:
    """
    Retrieves the list of employeeId values for employees who report to the given manager.
    Queries `employee_employment_histories` where isCurrent=True and deletedAt=None.
    Supports both direct employeeId and employee _id references as reportingManagerEmployeeId.
    """
    manager_ids = await get_manager_identifiers(db, manager_employee_id)
    
    # Query current employment histories
    query = {
        "isCurrent": True,
        "deletedAt": None,
        "reportingManagerEmployeeId": {"$in": manager_ids}
    }

    histories = await db.employee_employment_histories.find(query, {"employeeId": 1}).to_list(length=None)
    reporting_ids: Set[str] = {str(h["employeeId"]) for h in histories if h.get("employeeId")}

    if include_self and manager_employee_id:
        for m_id in manager_ids:
            if not (len(m_id) == 24 and not m_id.isdigit()):
                reporting_ids.add(m_id)

    return sorted(list(reporting_ids))
