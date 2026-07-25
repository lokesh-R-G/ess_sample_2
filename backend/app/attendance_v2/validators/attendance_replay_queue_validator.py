from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.attendance_replay_queue import AttendanceReplayQueueCreate, AttendanceReplayQueueUpdate

class AttendanceReplayQueueValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_replay_queues"]
        
    async def validate_create(self, data: AttendanceReplayQueueCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendanceReplayQueueUpdate):
        pass 
