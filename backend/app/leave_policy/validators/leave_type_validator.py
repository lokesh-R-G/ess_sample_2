from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.schemas.leave_type import LeaveTypeCreate, LeaveTypeUpdate

class LeaveTypeValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_types"]
        
    async def validate_create(self, data: LeaveTypeCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveTypeUpdate):
        pass 
