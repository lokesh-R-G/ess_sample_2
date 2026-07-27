from motor.motor_asyncio import AsyncIOMotorDatabase
from app.deduction_policy.repositories.base_repository import BaseRepository
from app.deduction_policy.models.pf_ceiling_config import PfCeilingConfigModel

class PfCeilingConfigRepository(BaseRepository[PfCeilingConfigModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "pf_ceiling_configs", PfCeilingConfigModel)
