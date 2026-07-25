from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.labour_welfare_fund_config import LabourWelfareFundConfigModel

class LabourWelfareFundConfigRepository(BaseRepository[LabourWelfareFundConfigModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "labour_welfare_fund_configs", LabourWelfareFundConfigModel)
