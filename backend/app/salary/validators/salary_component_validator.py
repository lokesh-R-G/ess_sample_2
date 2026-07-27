from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.schemas.salary_component import SalaryComponentCreate, SalaryComponentUpdate

class SalaryComponentValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["salary_components"]
        
    async def validate_create(self, data: SalaryComponentCreate):
        pass
            
    async def validate_update(self, id: str, data: SalaryComponentUpdate):
        pass 
