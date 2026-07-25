from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.attendance_closing import AttendanceClosingCreate, AttendanceClosingUpdate

class AttendanceClosingValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_closing"]
        
    async def validate_create(self, data: AttendanceClosingCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendanceClosingUpdate):
        pass 
