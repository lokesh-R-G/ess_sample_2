from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.employee_document import EmployeeDocumentCreate, EmployeeDocumentUpdate
from bson import ObjectId

class EmployeeDocumentValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_documents"]
        
    async def validate_create(self, data: EmployeeDocumentCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeDocumentUpdate):
        pass 
