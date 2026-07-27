from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.schemas.leave_cancellation import LeaveCancellationCreate, LeaveCancellationUpdate

class LeaveCancellationValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_cancellations"]
        
    async def validate_create(self, data: LeaveCancellationCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveCancellationUpdate):
        pass 
