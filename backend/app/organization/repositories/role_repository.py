from motor.motor_asyncio import AsyncIOMotorDatabase
from app.organization.repositories.base_repository import BaseRepository
from app.organization.models.role import RoleModel

class RoleRepository(BaseRepository[RoleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "roles", RoleModel)
