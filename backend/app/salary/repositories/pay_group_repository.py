from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.pay_group import PayGroupModel

class PayGroupRepository(BaseRepository[PayGroupModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "pay_groups", PayGroupModel)
