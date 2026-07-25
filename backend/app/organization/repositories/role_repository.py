from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.role import RoleModel

class RoleRepository(BaseRepository[RoleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "roles", RoleModel)
