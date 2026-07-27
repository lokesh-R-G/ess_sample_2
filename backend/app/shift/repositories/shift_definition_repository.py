from motor.motor_asyncio import AsyncIOMotorDatabase
from app.shift.repositories.base_repository import BaseRepository
from app.shift.models.shift_definition import ShiftDefinitionModel

class ShiftDefinitionRepository(BaseRepository[ShiftDefinitionModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'shift_definitions', ShiftDefinitionModel)
