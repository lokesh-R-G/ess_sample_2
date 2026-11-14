from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employment_history import EmploymentHistoryCreate, EmploymentHistoryUpdate
from app.employee.validators.employee_validator import EmployeeValidator
from bson import ObjectId

class EmploymentHistoryValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_employment_histories"]
        self.employee_validator = EmployeeValidator(db)

    async def _get_employee_code_for_employee(self, employee_id: str):
        employee = await self.db.employees.find_one({"employeeId": employee_id, "deletedAt": None, "isCurrent": {"$ne": False}})
        if not employee:
            return None
        return employee.get("employeeCode")

    async def validate_create(self, data: EmploymentHistoryCreate):
        if not data.companyId or not data.employeeId:
            return
        employee_code = await self._get_employee_code_for_employee(data.employeeId)
        if not employee_code:
            return
        await self.employee_validator.validate_company_scoped_employee_code(
            employee_code=employee_code,
            company_id=data.companyId,
            employee_id=data.employeeId,
        )

    async def validate_update(self, id: str, data: EmploymentHistoryUpdate):
        current = await self.collection.find_one({"_id": ObjectId(id), "deletedAt": None})
        if not current:
            return

        target_company = data.companyId if data.companyId is not None else current.get("companyId")
        if not target_company:
            return

        employee_id = current.get("employeeId")
        if not employee_id:
            return

        employee_code = await self._get_employee_code_for_employee(employee_id)
        if not employee_code:
            return

        await self.employee_validator.validate_company_scoped_employee_code(
            employee_code=employee_code,
            company_id=target_company,
            employee_id=employee_id,
        )
