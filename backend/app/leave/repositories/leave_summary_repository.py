from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave.repositories.base_repository import BaseRepository
from app.leave.models.leave_summary import LeaveSummaryModel

class LeaveSummaryRepository(BaseRepository[LeaveSummaryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_summarys", LeaveSummaryModel)
