from motor.motor_asyncio import AsyncIOMotorDatabase
from app.permission.repositories.base_repository import BaseRepository
from app.permission.models.permission_balance import PermissionBalanceModel

class PermissionBalanceRepository(BaseRepository[PermissionBalanceModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "permission_balances", PermissionBalanceModel)
