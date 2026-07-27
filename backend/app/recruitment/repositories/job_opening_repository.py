from motor.motor_asyncio import AsyncIOMotorDatabase
from app.recruitment.repositories.base_repository import BaseRepository
from app.recruitment.models.job_opening import JobOpeningModel

class JobOpeningRepository(BaseRepository[JobOpeningModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'job_openings', JobOpeningModel)
