from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employee_role_assignment import EmployeeRoleAssignmentCreate, EmployeeRoleAssignmentUpdate
from bson import ObjectId

class EmployeeRoleAssignmentValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_role_assignments"]
        
    async def validate_create(self, data: EmployeeRoleAssignmentCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeRoleAssignmentUpdate):
        pass 
