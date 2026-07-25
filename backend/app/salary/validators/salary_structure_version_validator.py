from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.salary_structure_version import SalaryStructureVersionCreate, SalaryStructureVersionUpdate

class SalaryStructureVersionValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["salary_structure_versions"]
        
    async def validate_create(self, data: SalaryStructureVersionCreate):
        pass
            
    async def validate_update(self, id: str, data: SalaryStructureVersionUpdate):
        pass 
