from motor.motor_asyncio import AsyncIOMotorDatabase
from app.permission.repositories.base_repository import BaseRepository
from app.permission.models.grace_request import GraceRequestModel

class GraceRequestRepository(BaseRepository[GraceRequestModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "grace_requests", GraceRequestModel)
