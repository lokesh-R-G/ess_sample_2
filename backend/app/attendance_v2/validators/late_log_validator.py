from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.late_log import LateLogCreate, LateLogUpdate

class LateLogValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["late_logs"]
        
    async def validate_create(self, data: LateLogCreate):
        pass
            
    async def validate_update(self, id: str, data: LateLogUpdate):
        pass 
