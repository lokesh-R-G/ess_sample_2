from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.permission.schemas.grace_request import GraceRequestCreate, GraceRequestUpdate

class GraceRequestValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["grace_requests"]
        
    async def validate_create(self, data: GraceRequestCreate):
        pass
            
    async def validate_update(self, id: str, data: GraceRequestUpdate):
        pass 
