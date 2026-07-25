from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_summary import LeaveSummaryModel

class LeaveSummaryRepository(BaseRepository[LeaveSummaryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_summarys", LeaveSummaryModel)
