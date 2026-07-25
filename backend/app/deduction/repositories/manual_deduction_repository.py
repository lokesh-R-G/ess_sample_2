from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.manual_deduction import ManualDeductionModel

class ManualDeductionRepository(BaseRepository[ManualDeductionModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "manual_deductions", ManualDeductionModel)
