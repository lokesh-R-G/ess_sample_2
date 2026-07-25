from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_summary import LeaveSummaryCreate, LeaveSummaryUpdate

class LeaveSummaryValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_summarys"]
        
    async def validate_create(self, data: LeaveSummaryCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveSummaryUpdate):
        pass 
