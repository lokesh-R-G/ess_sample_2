from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.comp_off_balance import CompOffBalanceModel

class CompOffBalanceRepository(BaseRepository[CompOffBalanceModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "comp_off_balances", CompOffBalanceModel)
