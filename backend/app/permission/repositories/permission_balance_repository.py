from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.permission_balance import PermissionBalanceModel

class PermissionBalanceRepository(BaseRepository[PermissionBalanceModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "permission_balances", PermissionBalanceModel)
