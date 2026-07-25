from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.grace_approval import GraceApprovalModel

class GraceApprovalRepository(BaseRepository[GraceApprovalModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "grace_approvals", GraceApprovalModel)
