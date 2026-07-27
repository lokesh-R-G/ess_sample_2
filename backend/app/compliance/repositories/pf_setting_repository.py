from motor.motor_asyncio import AsyncIOMotorDatabase
from app.compliance.repositories.base_repository import BaseRepository
from app.compliance.models.pf_setting import PfSettingModel

class PfSettingRepository(BaseRepository[PfSettingModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'pf_settings', PfSettingModel)
