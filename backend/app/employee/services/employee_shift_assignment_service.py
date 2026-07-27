from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.repositories.employee_shift_assignment_repository import EmployeeShiftAssignmentRepository
from app.employee.validators.employee_shift_assignment_validator import EmployeeShiftAssignmentValidator
from app.employee.schemas.employee_shift_assignment import EmployeeShiftAssignmentCreate, EmployeeShiftAssignmentUpdate
from app.employee.models.employee_shift_assignment import EmployeeShiftAssignmentModel

class EmployeeShiftAssignmentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeShiftAssignmentRepository(db)
        self.validator = EmployeeShiftAssignmentValidator(db)
        
    async def create(self, data: EmployeeShiftAssignmentCreate, user_id: str = None) -> EmployeeShiftAssignmentModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeShiftAssignmentModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeShiftAssignmentUpdate, user_id: str = None) -> Optional[EmployeeShiftAssignmentModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
