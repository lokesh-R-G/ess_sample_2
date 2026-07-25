from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.holiday import HolidayModel

class HolidayRepository(BaseRepository[HolidayModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "holidays", HolidayModel)
