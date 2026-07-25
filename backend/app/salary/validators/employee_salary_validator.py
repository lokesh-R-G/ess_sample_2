from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.employee_salary import EmployeeSalaryCreate, EmployeeSalaryUpdate

class EmployeeSalaryValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_salarys"]
        
    async def validate_create(self, data: EmployeeSalaryCreate):
        pass
            
    async def validate_update(self, id: str, data: EmployeeSalaryUpdate):
        pass 
