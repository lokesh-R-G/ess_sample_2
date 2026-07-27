from motor.motor_asyncio import AsyncIOMotorDatabase
from app.reimbursement.repositories.base_repository import BaseRepository
from app.reimbursement.models.employee_reimbursement import EmployeeReimbursementModel

class EmployeeReimbursementRepository(BaseRepository[EmployeeReimbursementModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'employee_reimbursements', EmployeeReimbursementModel)
