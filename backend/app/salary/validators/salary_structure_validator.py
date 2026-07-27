from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.schemas.salary_structure import SalaryStructureCreate, SalaryStructureUpdate

class SalaryStructureValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["salary_structures"]
        
    async def validate_create(self, data: SalaryStructureCreate):
        pass
            
    async def validate_update(self, id: str, data: SalaryStructureUpdate):
        pass 
