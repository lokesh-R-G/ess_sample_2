from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_encashment import LeaveEncashmentCreate, LeaveEncashmentUpdate

class LeaveEncashmentValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_encashments"]
        
    async def validate_create(self, data: LeaveEncashmentCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveEncashmentUpdate):
        pass 
