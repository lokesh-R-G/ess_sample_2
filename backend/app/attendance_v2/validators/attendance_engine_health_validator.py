from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.attendance_engine_health import AttendanceEngineHealthCreate, AttendanceEngineHealthUpdate

class AttendanceEngineHealthValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_engine_health"]
        
    async def validate_create(self, data: AttendanceEngineHealthCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendanceEngineHealthUpdate):
        pass 
