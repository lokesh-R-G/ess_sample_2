from motor.motor_asyncio import AsyncIOMotorDatabase
from app.permission.repositories.base_repository import BaseRepository
from app.permission.models.grace_balance import GraceBalanceModel

class GraceBalanceRepository(BaseRepository[GraceBalanceModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "grace_balances", GraceBalanceModel)
