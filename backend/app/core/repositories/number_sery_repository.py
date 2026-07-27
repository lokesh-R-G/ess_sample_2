from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.repositories.base_repository import BaseRepository
from app.core.models.number_sery import NumberSeryModel

class NumberSeryRepository(BaseRepository[NumberSeryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'number_series', NumberSeryModel)
