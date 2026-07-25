from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.pf_ceiling_config import PfCeilingConfigModel

class PfCeilingConfigRepository(BaseRepository[PfCeilingConfigModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "pf_ceiling_configs", PfCeilingConfigModel)
