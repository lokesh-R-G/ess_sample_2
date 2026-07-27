from motor.motor_asyncio import AsyncIOMotorDatabase
from app.compliance.repositories.base_repository import BaseRepository
from app.compliance.models.pt_setting import PtSettingModel

class PtSettingRepository(BaseRepository[PtSettingModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'pt_settings', PtSettingModel)
