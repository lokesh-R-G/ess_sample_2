from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.schemas.leave_year_configuration import LeaveYearConfigurationCreate, LeaveYearConfigurationUpdate

class LeaveYearConfigurationValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_year_configurations"]
        
    async def validate_create(self, data: LeaveYearConfigurationCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveYearConfigurationUpdate):
        pass 
