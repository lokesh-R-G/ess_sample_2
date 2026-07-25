from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.esi_config import EsiConfigModel

class EsiConfigRepository(BaseRepository[EsiConfigModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "esi_configs", EsiConfigModel)
