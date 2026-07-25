from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.employee_salary_history import EmployeeSalaryHistoryCreate, EmployeeSalaryHistoryUpdate

class EmployeeSalaryHistoryValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_salary_history"]
        
    async def validate_create(self, data: EmployeeSalaryHistoryCreate):
        pass
            
    async def validate_update(self, id: str, data: EmployeeSalaryHistoryUpdate):
        pass 
