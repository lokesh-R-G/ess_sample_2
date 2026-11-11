from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession
from fastapi import HTTPException
from app.employee.schemas.employee import EmployeeCreate, EmployeeUpdate
from bson import ObjectId
from typing import Optional

class EmployeeValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employees"]
        
    async def validate_create(
        self,
        data: EmployeeCreate,
        master_employee_id: Optional[str] = None,
        session: Optional[AsyncIOMotorClientSession] = None
    ):
        """
        Validates proposed employee creation fields.
        Exact Business Rule:
        Machine ID must not match any of (employeeId, employeeCode, empId, machineId)
        belonging to another employee.
        Matching identifiers within the same employee (e.g. machineId == employeeCode) are permitted.
        """
        if data.machineId is not None:
            raw_mid = str(data.machineId).strip()
            if raw_mid:
                # Query for any existing current/active employee matching raw_mid in any of the 4 fields
                query = {
                    "$or": [
                        {"machineId": raw_mid},
                        {"employeeId": raw_mid},
                        {"employeeCode": raw_mid},
                        {"empId": raw_mid}
                    ],
                    "deletedAt": None,
                    "isCurrent": {"$ne": False}
                }
                if master_employee_id:
                    query["masterEmployeeId"] = {"$ne": master_employee_id}

                existing = await self.collection.find_one(query, session=session)
                if existing:
                    conflicting_field = "identifier"
                    for f in ["machineId", "employeeId", "employeeCode", "empId"]:
                        if str(existing.get(f)).strip() == raw_mid:
                            conflicting_field = f
                            break
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            f"Machine ID '{raw_mid}' conflicts with {conflicting_field} "
                            f"of employee {existing.get('employeeCode') or existing.get('employeeId')} ({existing.get('status', 'Active')})."
                        )
                    )
            
    async def validate_update(
        self,
        id: str,
        data: EmployeeUpdate,
        master_employee_id: Optional[str] = None,
        session: Optional[AsyncIOMotorClientSession] = None
    ):
        """
        Validates proposed employee update fields.
        Excludes the current employee using authoritative masterEmployeeId or _id.
        """
        if data.machineId is not None:
            raw_mid = str(data.machineId).strip()
            if raw_mid:
                # Find current doc if master_employee_id not passed
                if not master_employee_id:
                    curr_query = {"_id": ObjectId(id)} if ObjectId.is_valid(id) else {"employeeId": id}
                    curr = await self.collection.find_one(curr_query, session=session)
                    if curr:
                        master_employee_id = curr.get("masterEmployeeId") or str(curr.get("_id"))

                and_clauses = [
                    {
                        "$or": [
                            {"machineId": raw_mid},
                            {"employeeId": raw_mid},
                            {"employeeCode": raw_mid},
                            {"empId": raw_mid}
                        ]
                    },
                    {"deletedAt": None},
                    {"isCurrent": {"$ne": False}}
                ]

                if master_employee_id:
                    and_clauses.append({"masterEmployeeId": {"$ne": master_employee_id}})
                else:
                    if ObjectId.is_valid(id):
                        and_clauses.append({"_id": {"$ne": ObjectId(id)}})
                    and_clauses.append({"employeeId": {"$ne": id}})

                existing = await self.collection.find_one({"$and": and_clauses}, session=session)
                if existing:
                    conflicting_field = "identifier"
                    for f in ["machineId", "employeeId", "employeeCode", "empId"]:
                        if str(existing.get(f)).strip() == raw_mid:
                            conflicting_field = f
                            break
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            f"Machine ID '{raw_mid}' conflicts with {conflicting_field} "
                            f"of another employee {existing.get('employeeCode') or existing.get('employeeId')} ({existing.get('status', 'Active')})."
                        )
                    )

        # Also validate if employeeCode is being changed on an update
        if data.employeeCode is not None:
            raw_code = str(data.employeeCode).strip()
            if raw_code:
                # Check if this employeeCode conflicts with another employee's machineId
                if not master_employee_id:
                    curr_query = {"_id": ObjectId(id)} if ObjectId.is_valid(id) else {"employeeId": id}
                    curr = await self.collection.find_one(curr_query, session=session)
                    if curr:
                        master_employee_id = curr.get("masterEmployeeId") or str(curr.get("_id"))

                and_clauses = [
                    {"machineId": raw_code},
                    {"deletedAt": None},
                    {"isCurrent": {"$ne": False}}
                ]
                if master_employee_id:
                    and_clauses.append({"masterEmployeeId": {"$ne": master_employee_id}})
                else:
                    if ObjectId.is_valid(id):
                        and_clauses.append({"_id": {"$ne": ObjectId(id)}})
                    and_clauses.append({"employeeId": {"$ne": id}})

                conflict = await self.collection.find_one({"$and": and_clauses}, session=session)
                if conflict:
                    raise HTTPException(
                        status_code=409,
                        detail=f"Employee Code '{raw_code}' conflicts with machineId of employee {conflict.get('employeeCode') or conflict.get('employeeId')}."
                    )
