from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.grace_balance import GraceBalanceModel

class GraceBalanceRepository(BaseRepository[GraceBalanceModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "grace_balances", GraceBalanceModel)
