from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.services.employee_shift_assignment_service import EmployeeShiftAssignmentService
from app.employee.schemas.employee_shift_assignment import EmployeeShiftAssignmentCreate, EmployeeShiftAssignmentUpdate, EmployeeShiftAssignmentResponse
from app.employee.models.employee_shift_assignment import EmployeeShiftAssignmentModel

class EmployeeShiftAssignmentController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeShiftAssignmentService(db)
        
    async def create(self, data: EmployeeShiftAssignmentCreate, user_id: str) -> EmployeeShiftAssignmentModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeShiftAssignmentModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeShiftAssignment not found")
        return doc
        
    async def update(self, id: str, data: EmployeeShiftAssignmentUpdate, user_id: str) -> EmployeeShiftAssignmentModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeShiftAssignment not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeShiftAssignment not found")
        return {"message": "EmployeeShiftAssignment archived successfully"}
