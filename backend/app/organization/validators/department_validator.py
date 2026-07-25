from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.department import DepartmentCreate, DepartmentUpdate
from bson import ObjectId

class DepartmentValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["departments"]
        
    async def validate_create(self, data: DepartmentCreate):
        query = {"name": data.name, "deletedAt": None}
        if hasattr(data, 'companyId') and data.companyId:
            query["companyId"] = data.companyId
            parent = await self.db["companies"].find_one({"_id": ObjectId(data.companyId), "deletedAt": None})
            if not parent:
                raise HTTPException(status_code=400, detail="Parent company not found or archived")
        if await self.collection.find_one(query):
            raise HTTPException(status_code=409, detail=f"Department with this name already exists")
            
    async def validate_update(self, id: str, data: DepartmentUpdate):
        pass # Optional update validation
