from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_cancellation import LeaveCancellationModel

class LeaveCancellationRepository(BaseRepository[LeaveCancellationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_cancellations", LeaveCancellationModel)
