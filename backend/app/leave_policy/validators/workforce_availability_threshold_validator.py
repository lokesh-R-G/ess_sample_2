from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.workforce_availability_threshold import WorkforceAvailabilityThresholdCreate, WorkforceAvailabilityThresholdUpdate

class WorkforceAvailabilityThresholdValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["workforce_availability_thresholds"]
        
    async def validate_create(self, data: WorkforceAvailabilityThresholdCreate):
        pass
            
    async def validate_update(self, id: str, data: WorkforceAvailabilityThresholdUpdate):
        pass 
