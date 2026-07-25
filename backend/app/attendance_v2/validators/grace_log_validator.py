from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.grace_log import GraceLogCreate, GraceLogUpdate

class GraceLogValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["grace_logs"]
        
    async def validate_create(self, data: GraceLogCreate):
        pass
            
    async def validate_update(self, id: str, data: GraceLogUpdate):
        pass 
