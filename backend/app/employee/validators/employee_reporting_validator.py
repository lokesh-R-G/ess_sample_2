from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employee_reporting import EmployeeReportingCreate, EmployeeReportingUpdate
from bson import ObjectId

class EmployeeReportingValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_reportings"]
        
    async def validate_create(self, data: EmployeeReportingCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeReportingUpdate):
        pass 
