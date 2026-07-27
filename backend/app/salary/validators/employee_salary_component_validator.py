from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.schemas.employee_salary_component import EmployeeSalaryComponentCreate, EmployeeSalaryComponentUpdate

class EmployeeSalaryComponentValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_salary_components"]
        
    async def validate_create(self, data: EmployeeSalaryComponentCreate):
        pass
            
    async def validate_update(self, id: str, data: EmployeeSalaryComponentUpdate):
        pass 
