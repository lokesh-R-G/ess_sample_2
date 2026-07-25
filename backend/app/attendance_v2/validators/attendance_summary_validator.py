from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.attendance_summary import AttendanceSummaryCreate, AttendanceSummaryUpdate

class AttendanceSummaryValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_summarys"]
        
    async def validate_create(self, data: AttendanceSummaryCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendanceSummaryUpdate):
        pass 
