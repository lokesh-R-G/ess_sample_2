from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_calendar import LeaveCalendarCreate, LeaveCalendarUpdate

class LeaveCalendarValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_calendars"]
        
    async def validate_create(self, data: LeaveCalendarCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveCalendarUpdate):
        pass 
