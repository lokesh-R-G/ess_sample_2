from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.schemas.salary_structure_component import SalaryStructureComponentCreate, SalaryStructureComponentUpdate

class SalaryStructureComponentValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["salary_structure_components"]
        
    async def validate_create(self, data: SalaryStructureComponentCreate):
        pass
            
    async def validate_update(self, id: str, data: SalaryStructureComponentUpdate):
        pass 
