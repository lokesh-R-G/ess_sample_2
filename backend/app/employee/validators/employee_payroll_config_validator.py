from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employee_payroll_config import EmployeePayrollConfigCreate, EmployeePayrollConfigUpdate

class EmployeePayrollConfigValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    async def validate_create(self, data: EmployeePayrollConfigCreate):
        pass
        
    async def validate_update(self, id: str, data: EmployeePayrollConfigUpdate):
        pass
