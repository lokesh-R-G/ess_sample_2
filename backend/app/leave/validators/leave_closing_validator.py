from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.schemas.leave_closing import LeaveClosingCreate, LeaveClosingUpdate

class LeaveClosingValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_closings"]
        
    async def validate_create(self, data: LeaveClosingCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveClosingUpdate):
        pass 
