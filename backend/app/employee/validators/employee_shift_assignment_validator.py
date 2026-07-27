from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employee_shift_assignment import EmployeeShiftAssignmentCreate, EmployeeShiftAssignmentUpdate
from bson import ObjectId

class EmployeeShiftAssignmentValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_shift_assignments"]
        
    async def validate_create(self, data: EmployeeShiftAssignmentCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeShiftAssignmentUpdate):
        pass 
