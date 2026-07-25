from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_year_configuration import LeaveYearConfigurationModel

class LeaveYearConfigurationRepository(BaseRepository[LeaveYearConfigurationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_year_configurations", LeaveYearConfigurationModel)
