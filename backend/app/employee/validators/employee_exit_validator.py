from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employee_exit import EmployeeExitCreate, EmployeeExitUpdate
from bson import ObjectId

class EmployeeExitValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_exits"]
        
    async def validate_create(self, data: EmployeeExitCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeExitUpdate):
        pass 
