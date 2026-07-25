from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.attendance import AttendanceCreate, AttendanceUpdate

class AttendanceValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendances"]
        
    async def validate_create(self, data: AttendanceCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendanceUpdate):
        pass 
