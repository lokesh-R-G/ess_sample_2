from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.attendance_exception import AttendanceExceptionCreate, AttendanceExceptionUpdate

class AttendanceExceptionValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_exceptions"]
        
    async def validate_create(self, data: AttendanceExceptionCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendanceExceptionUpdate):
        pass 
