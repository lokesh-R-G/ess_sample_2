from motor.motor_asyncio import AsyncIOMotorDatabase
from app.shift.repositories.base_repository import BaseRepository
from app.shift.models.shift_group import ShiftGroupModel

class ShiftGroupRepository(BaseRepository[ShiftGroupModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'shift_groups', ShiftGroupModel)
