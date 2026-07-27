from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave.repositories.base_repository import BaseRepository
from app.leave.models.leave_application import LeaveApplicationModel

class LeaveApplicationRepository(BaseRepository[LeaveApplicationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_applications", LeaveApplicationModel)
