from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.cost_center import CostCenterCreate, CostCenterUpdate

class CostCenterValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["cost_centers"]
        
    async def validate_create(self, data: CostCenterCreate):
        pass
            
    async def validate_update(self, id: str, data: CostCenterUpdate):
        pass 
