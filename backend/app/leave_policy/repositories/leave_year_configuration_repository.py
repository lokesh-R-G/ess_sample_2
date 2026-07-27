from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave_policy.repositories.base_repository import BaseRepository
from app.leave_policy.models.leave_year_configuration import LeaveYearConfigurationModel

class LeaveYearConfigurationRepository(BaseRepository[LeaveYearConfigurationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_year_configurations", LeaveYearConfigurationModel)
