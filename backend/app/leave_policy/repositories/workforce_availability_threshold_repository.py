from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.workforce_availability_threshold import WorkforceAvailabilityThresholdModel

class WorkforceAvailabilityThresholdRepository(BaseRepository[WorkforceAvailabilityThresholdModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "workforce_availability_thresholds", WorkforceAvailabilityThresholdModel)
