from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.employee_shift_assignment import EmployeeShiftAssignmentModel

class EmployeeShiftAssignmentRepository(BaseRepository[EmployeeShiftAssignmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_shift_assignments", EmployeeShiftAssignmentModel)
