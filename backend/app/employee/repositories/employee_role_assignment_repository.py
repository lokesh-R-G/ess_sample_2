from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.employee.models.employee_role_assignment import EmployeeRoleAssignmentModel

class EmployeeRoleAssignmentRepository(BaseRepository[EmployeeRoleAssignmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_role_assignments", EmployeeRoleAssignmentModel)
