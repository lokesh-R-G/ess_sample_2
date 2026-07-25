from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.expense_type_config import ExpenseTypeConfigModel

class ExpenseTypeConfigRepository(BaseRepository[ExpenseTypeConfigModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "expense_type_configs", ExpenseTypeConfigModel)
