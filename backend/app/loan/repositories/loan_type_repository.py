from motor.motor_asyncio import AsyncIOMotorDatabase
from app.loan.repositories.base_repository import BaseRepository
from app.loan.models.loan_type import LoanTypeModel

class LoanTypeRepository(BaseRepository[LoanTypeModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'loan_types', LoanTypeModel)
