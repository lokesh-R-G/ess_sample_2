from motor.motor_asyncio import AsyncIOMotorDatabase
from app.expense.repositories.base_repository import BaseRepository
from app.expense.models.expense_category import ExpenseCategoryModel

class ExpenseCategoryRepository(BaseRepository[ExpenseCategoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'expense_categories', ExpenseCategoryModel)
