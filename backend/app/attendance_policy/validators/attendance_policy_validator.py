from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.attendance_policy import AttendancePolicyCreate, AttendancePolicyUpdate

class AttendancePolicyValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_policys"]
        
    async def validate_create(self, data: AttendancePolicyCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendancePolicyUpdate):
        pass 
