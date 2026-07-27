from motor.motor_asyncio import AsyncIOMotorDatabase
from app.reimbursement_policy.repositories.base_repository import BaseRepository
from app.reimbursement_policy.models.expense_type_config import ExpenseTypeConfigModel

class ExpenseTypeConfigRepository(BaseRepository[ExpenseTypeConfigModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "expense_type_configs", ExpenseTypeConfigModel)
