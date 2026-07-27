from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.schemas.leave_adjustment import LeaveAdjustmentCreate, LeaveAdjustmentUpdate

class LeaveAdjustmentValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_adjustments"]
        
    async def validate_create(self, data: LeaveAdjustmentCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveAdjustmentUpdate):
        pass 
