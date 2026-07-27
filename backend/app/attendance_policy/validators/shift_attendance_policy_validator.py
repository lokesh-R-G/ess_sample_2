from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_policy.schemas.shift_attendance_policy import ShiftAttendancePolicyCreate, ShiftAttendancePolicyUpdate

class ShiftAttendancePolicyValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["shift_attendance_policys"]
        
    async def validate_create(self, data: ShiftAttendancePolicyCreate):
        pass
            
    async def validate_update(self, id: str, data: ShiftAttendancePolicyUpdate):
        pass 
