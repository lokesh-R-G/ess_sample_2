from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.schemas.leave_application import LeaveApplicationCreate, LeaveApplicationUpdate

class LeaveApplicationValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_applications"]
        
    async def validate_create(self, data: LeaveApplicationCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveApplicationUpdate):
        pass 
