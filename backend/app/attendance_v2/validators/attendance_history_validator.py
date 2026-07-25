from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.attendance_history import AttendanceHistoryCreate, AttendanceHistoryUpdate

class AttendanceHistoryValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_history"]
        
    async def validate_create(self, data: AttendanceHistoryCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendanceHistoryUpdate):
        pass 
