from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_history import LeaveHistoryCreate, LeaveHistoryUpdate

class LeaveHistoryValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_history"]
        
    async def validate_create(self, data: LeaveHistoryCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveHistoryUpdate):
        pass 
