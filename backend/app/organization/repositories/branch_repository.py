from motor.motor_asyncio import AsyncIOMotorDatabase
from app.organization.repositories.base_repository import BaseRepository
from app.organization.models.branch import BranchModel

class BranchRepository(BaseRepository[BranchModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "branchs", BranchModel)
