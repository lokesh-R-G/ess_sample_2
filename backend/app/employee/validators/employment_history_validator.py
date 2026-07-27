from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employment_history import EmploymentHistoryCreate, EmploymentHistoryUpdate
from bson import ObjectId

class EmploymentHistoryValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employment_history"]
        
    async def validate_create(self, data: EmploymentHistoryCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmploymentHistoryUpdate):
        pass 
