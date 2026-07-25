from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.monthly_attendance import MonthlyAttendanceCreate, MonthlyAttendanceUpdate

class MonthlyAttendanceValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["monthly_attendances"]
        
    async def validate_create(self, data: MonthlyAttendanceCreate):
        pass
            
    async def validate_update(self, id: str, data: MonthlyAttendanceUpdate):
        pass 
