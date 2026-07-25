from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.attendance_calculation import AttendanceCalculationCreate, AttendanceCalculationUpdate

class AttendanceCalculationValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_calculations"]
        
    async def validate_create(self, data: AttendanceCalculationCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendanceCalculationUpdate):
        pass 
