from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.permission_overflow_rule import PermissionOverflowRuleModel

class PermissionOverflowRuleRepository(BaseRepository[PermissionOverflowRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "permission_overflow_rules", PermissionOverflowRuleModel)
