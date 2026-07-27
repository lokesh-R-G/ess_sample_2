from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave.repositories.base_repository import BaseRepository
from app.leave.models.leave_cancellation import LeaveCancellationModel

class LeaveCancellationRepository(BaseRepository[LeaveCancellationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_cancellations", LeaveCancellationModel)
