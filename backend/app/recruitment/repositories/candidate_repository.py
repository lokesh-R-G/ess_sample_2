from motor.motor_asyncio import AsyncIOMotorDatabase
from app.recruitment.repositories.base_repository import BaseRepository
from app.recruitment.models.candidate import CandidateModel

class CandidateRepository(BaseRepository[CandidateModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'candidates', CandidateModel)
