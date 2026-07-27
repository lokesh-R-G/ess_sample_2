from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employee_emergency_contact import EmployeeEmergencyContactCreate, EmployeeEmergencyContactUpdate
from bson import ObjectId

class EmployeeEmergencyContactValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_emergency_contacts"]
        
    async def validate_create(self, data: EmployeeEmergencyContactCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeEmergencyContactUpdate):
        pass 
