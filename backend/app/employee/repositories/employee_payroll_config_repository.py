from app.employee.repositories.base_repository import BaseRepository
from app.employee.models.employee_payroll_config import EmployeePayrollConfigModel

class EmployeePayrollConfigRepository(BaseRepository[EmployeePayrollConfigModel]):
    def __init__(self):
        super().__init__(EmployeePayrollConfigModel, "employee_payroll_configs")
