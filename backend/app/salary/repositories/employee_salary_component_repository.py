from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.salary.models.employee_salary_component import EmployeeSalaryComponentModel

class EmployeeSalaryComponentRepository(BaseRepository[EmployeeSalaryComponentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_salary_components", EmployeeSalaryComponentModel)

    async def get_components_by_employee_and_date(self, employee_id: str, target_date: datetime) -> list[dict]:
        """
        Resolves the full salary structure active for an employee on a given date.
        """
        query = {
            "employeeId": employee_id,
            "deletedAt": None,
            "effectiveFrom": {"$lte": target_date},
            "$or": [
                {"effectiveTo": None},
                {"effectiveTo": {"$gt": target_date}}
            ]
        }
        
        # We return dicts here because the engine consumes dicts
        cursor = self.collection.find(query, sort=[("version", -1)])
        docs = await cursor.to_list(length=None)
        
        # In case of overlapping versions (which shouldn't happen), deduplicate by salaryComponentId keeping highest version
        seen = set()
        final_docs = []
        for doc in docs:
            cid = str(doc.get("salaryComponentId"))
            if cid not in seen:
                seen.add(cid)
                doc["_id"] = str(doc["_id"])
                final_docs.append(doc)
                
        return final_docs
