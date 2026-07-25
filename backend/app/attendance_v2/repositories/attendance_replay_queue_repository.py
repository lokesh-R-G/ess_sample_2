from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.attendance_replay_queue import AttendanceReplayQueueModel

class AttendanceReplayQueueRepository(BaseRepository[AttendanceReplayQueueModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_replay_queues", AttendanceReplayQueueModel)
