from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_balance import LeaveBalanceModel

class LeaveBalanceRepository(BaseRepository[LeaveBalanceModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_balances", LeaveBalanceModel)
