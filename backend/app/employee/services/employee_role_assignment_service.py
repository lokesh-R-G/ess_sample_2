from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.repositories.employee_role_assignment_repository import EmployeeRoleAssignmentRepository
from app.employee.validators.employee_role_assignment_validator import EmployeeRoleAssignmentValidator
from app.employee.schemas.employee_role_assignment import EmployeeRoleAssignmentCreate, EmployeeRoleAssignmentUpdate
from app.employee.models.employee_role_assignment import EmployeeRoleAssignmentModel

class EmployeeRoleAssignmentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeRoleAssignmentRepository(db)
        self.validator = EmployeeRoleAssignmentValidator(db)
        
    async def create(self, data: EmployeeRoleAssignmentCreate, user_id: str = None) -> EmployeeRoleAssignmentModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeRoleAssignmentModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeRoleAssignmentUpdate, user_id: str = None) -> Optional[EmployeeRoleAssignmentModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
