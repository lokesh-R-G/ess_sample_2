from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.employee_role_assignment import EmployeeRoleAssignmentModel

class EmployeeRoleAssignmentRepository(BaseRepository[EmployeeRoleAssignmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_role_assignments", EmployeeRoleAssignmentModel)
