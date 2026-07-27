from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.schemas.attendance_adjustment import AttendanceAdjustmentCreate, AttendanceAdjustmentUpdate

class AttendanceAdjustmentValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_adjustments"]
        
    async def validate_create(self, data: AttendanceAdjustmentCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendanceAdjustmentUpdate):
        pass 
