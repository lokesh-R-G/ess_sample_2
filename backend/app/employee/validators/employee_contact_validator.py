from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.employee_contact import EmployeeContactCreate, EmployeeContactUpdate
from bson import ObjectId

class EmployeeContactValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_contacts"]
        
    async def validate_create(self, data: EmployeeContactCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeContactUpdate):
        pass 
