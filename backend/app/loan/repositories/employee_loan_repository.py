from motor.motor_asyncio import AsyncIOMotorDatabase
from app.loan.repositories.base_repository import BaseRepository
from app.loan.models.employee_loan import EmployeeLoanModel

class EmployeeLoanRepository(BaseRepository[EmployeeLoanModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'employee_loans', EmployeeLoanModel)
