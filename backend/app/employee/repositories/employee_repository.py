from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
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
                "from": "employee_employment_histories",
                "let": {"empId": "$employeeId"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$employeeId", "$$empId"]}, {"$eq": ["$isCurrent", True]}]}}}
                ],
                "as": "employment"
            }},
            {"$unwind": {"path": "$personal", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$employment", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "employeeId": 1,
                "employeeCode": 1,
                "systemAccessEnabled": 1,
                "essStatus": 1,
                "authUserId": 1,
                "status": 1,
                "firstName": "$personal.firstName",
                "lastName": "$personal.lastName",
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
