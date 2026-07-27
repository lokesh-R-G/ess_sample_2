from motor.motor_asyncio import AsyncIOMotorDatabase
from app.recruitment.repositories.base_repository import BaseRepository
from app.recruitment.models.interview import InterviewModel

class InterviewRepository(BaseRepository[InterviewModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'interviews', InterviewModel)
