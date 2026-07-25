from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.branch import BranchModel

class BranchRepository(BaseRepository[BranchModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "branchs", BranchModel)
