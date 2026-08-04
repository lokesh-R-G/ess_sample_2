from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.employee.repositories.base_repository import BaseRepository
from app.employee.models.employee import EmployeeModel

class EmployeeRepository(BaseRepository[EmployeeModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employees", EmployeeModel)

    async def get_directory(self, skip: int = 0, limit: int = 100) -> dict:
        pipeline = [
            {"$match": {"deletedAt": None, "isCurrent": True}},
            {"$lookup": {
                "from": "employee_personals",
                "let": {"empId": "$employeeId"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$employeeId", "$$empId"]}, {"$eq": ["$isCurrent", True]}]}}}
                ],
                "as": "personal"
            }},
            {"$lookup": {
                "from": "employee_contacts",
                "let": {"empId": "$employeeId"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$employeeId", "$$empId"]}, {"$eq": ["$isCurrent", True]}]}}}
                ],
                "as": "contact"
            }},
            {"$lookup": {
                "from": "employee_employment_histories",
                "let": {"empId": "$employeeId"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$employeeId", "$$empId"]}, {"$eq": ["$isCurrent", True]}]}}}
                ],
                "as": "employment"
            }},
            {"$unwind": {"path": "$personal", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$contact", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$employment", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "_id": 0,
                "employeeId": {"$toString": "$employeeId"},
                "employeeCode": 1,
                "systemAccessEnabled": 1,
                "essStatus": 1,
                "authUserId": 1,
                "status": 1,
                "firstName": "$personal.firstName",
                "lastName": "$personal.lastName",
                "personalEmail": "$contact.personalEmail",
                "companyId": "$employment.companyId",
                "branchId": "$employment.branchId",
                "departmentId": "$employment.departmentId",
                "designationId": "$employment.designationId"
            }},
            {"$skip": skip},
            {"$limit": limit}
        ]

        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=None)

        total = await self.collection.count_documents({"deletedAt": None, "isCurrent": True})

        return {
            "data": docs,
            "total": total
        }

    async def get_by_employee_id(self, employee_id: str) -> Optional[EmployeeModel]:
        doc = await self.collection.find_one({
            "employeeId": employee_id,
            "deletedAt": None,
            "isCurrent": True
        })
        if doc:
            return self.model_class(**self._prepare_doc(doc))
        return None

    async def get_by_employee_code(self, employee_code: str) -> Optional[EmployeeModel]:
        doc = await self.collection.find_one({
            "employeeCode": employee_code,
            "deletedAt": None,
            "isCurrent": True
        })
        if doc:
            return self.model_class(**self._prepare_doc(doc))
        return None

    async def assign_employee_code(self, employee_id: str, employee_code: str) -> None:
        """
        Atomically assign an Employee Code to an Employee record.
        Used exclusively during the ESS invitation flow.
        Once an ESS account is created (essStatus != 'Not Invited'),
        the Employee Code is locked and cannot be changed via this method.
        """
        now = datetime.now(timezone.utc)
        await self.collection.update_one(
            {"employeeId": employee_id, "isCurrent": True, "deletedAt": None},
            {"$set": {"employeeCode": employee_code, "updatedAt": now}}
        )

    async def update_ess_status(
        self,
        employee_id: str,
        ess_status: str,
        auth_user_id: str,
        system_access_enabled: bool = True,
    ) -> None:
        """Write-back ESS provisioning state into the Employee V2 record."""
        now = datetime.now(timezone.utc)
        await self.collection.update_one(
            {"employeeId": employee_id, "isCurrent": True, "deletedAt": None},
            {"$set": {
                "essStatus": ess_status,
                "systemAccessEnabled": system_access_enabled,
                "authUserId": auth_user_id,
                "updatedAt": now,
            }}
        )
