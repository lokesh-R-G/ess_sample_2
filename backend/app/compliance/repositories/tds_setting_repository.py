from motor.motor_asyncio import AsyncIOMotorDatabase
from app.compliance.repositories.base_repository import BaseRepository
from app.compliance.models.tds_setting import TdsSettingModel

class TdsSettingRepository(BaseRepository[TdsSettingModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'tds_settings', TdsSettingModel)
