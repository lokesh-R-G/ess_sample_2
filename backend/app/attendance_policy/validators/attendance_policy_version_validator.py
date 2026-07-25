from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.attendance_policy_version import AttendancePolicyVersionCreate, AttendancePolicyVersionUpdate

class AttendancePolicyVersionValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_policy_versions"]
        
    async def validate_create(self, data: AttendancePolicyVersionCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendancePolicyVersionUpdate):
        pass 
