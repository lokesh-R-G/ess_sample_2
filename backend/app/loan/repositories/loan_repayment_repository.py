from motor.motor_asyncio import AsyncIOMotorDatabase
from app.loan.repositories.base_repository import BaseRepository
from app.loan.models.loan_repayment import LoanRepaymentModel

class LoanRepaymentRepository(BaseRepository[LoanRepaymentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'loan_repayments', LoanRepaymentModel)
