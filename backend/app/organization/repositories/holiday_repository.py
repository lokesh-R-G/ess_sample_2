from motor.motor_asyncio import AsyncIOMotorDatabase
from app.organization.repositories.base_repository import BaseRepository
from app.organization.models.holiday import HolidayModel

class HolidayRepository(BaseRepository[HolidayModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "holidays", HolidayModel)
