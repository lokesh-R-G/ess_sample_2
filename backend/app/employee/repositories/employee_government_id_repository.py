from app.employee.repositories.base_repository import BaseRepository
from app.employee.models.employee_government_id import EmployeeGovernmentIdModel

class EmployeeGovernmentIdRepository(BaseRepository[EmployeeGovernmentIdModel]):
    def __init__(self):
        super().__init__(EmployeeGovernmentIdModel, "employee_government_ids")
