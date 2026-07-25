from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.attendance_policy_history import AttendancePolicyHistoryCreate, AttendancePolicyHistoryUpdate

class AttendancePolicyHistoryValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_policy_history"]
        
    async def validate_create(self, data: AttendancePolicyHistoryCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendancePolicyHistoryUpdate):
        pass 
