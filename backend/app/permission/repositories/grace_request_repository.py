from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.grace_request import GraceRequestModel

class GraceRequestRepository(BaseRepository[GraceRequestModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "grace_requests", GraceRequestModel)
