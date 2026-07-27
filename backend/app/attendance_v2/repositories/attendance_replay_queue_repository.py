from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_v2.repositories.base_repository import BaseRepository
from app.attendance_v2.models.attendance_replay_queue import AttendanceReplayQueueModel

class AttendanceReplayQueueRepository(BaseRepository[AttendanceReplayQueueModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_replay_queues", AttendanceReplayQueueModel)
