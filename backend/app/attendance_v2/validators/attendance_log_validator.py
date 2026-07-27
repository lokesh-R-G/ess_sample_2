from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.schemas.attendance_log import AttendanceLogCreate, AttendanceLogUpdate

class AttendanceLogValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_logs"]
        
    async def validate_create(self, data: AttendanceLogCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendanceLogUpdate):
        pass 
