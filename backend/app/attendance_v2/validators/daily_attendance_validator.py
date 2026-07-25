from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.daily_attendance import DailyAttendanceCreate, DailyAttendanceUpdate

class DailyAttendanceValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["daily_attendances"]
        
    async def validate_create(self, data: DailyAttendanceCreate):
        pass
            
    async def validate_update(self, id: str, data: DailyAttendanceUpdate):
        pass 
