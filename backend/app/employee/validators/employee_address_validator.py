from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.employee_address import EmployeeAddressCreate, EmployeeAddressUpdate
from bson import ObjectId

class EmployeeAddressValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_address"]
        
    async def validate_create(self, data: EmployeeAddressCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeAddressUpdate):
        pass 
