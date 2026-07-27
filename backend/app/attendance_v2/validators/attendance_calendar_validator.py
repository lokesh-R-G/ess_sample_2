from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.schemas.attendance_calendar import AttendanceCalendarCreate, AttendanceCalendarUpdate

class AttendanceCalendarValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_calendars"]
        
    async def validate_create(self, data: AttendanceCalendarCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendanceCalendarUpdate):
        pass 
