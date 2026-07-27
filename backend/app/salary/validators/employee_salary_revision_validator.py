from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.schemas.employee_salary_revision import EmployeeSalaryRevisionCreate, EmployeeSalaryRevisionUpdate

class EmployeeSalaryRevisionValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_salary_revisions"]
        
    async def validate_create(self, data: EmployeeSalaryRevisionCreate):
        pass
            
    async def validate_update(self, id: str, data: EmployeeSalaryRevisionUpdate):
        pass 
