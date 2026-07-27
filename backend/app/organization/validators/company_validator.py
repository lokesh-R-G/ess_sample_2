from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.organization.schemas.company import CompanyCreate, CompanyUpdate
from bson import ObjectId

class CompanyValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["companys"]
        
    async def validate_create(self, data: CompanyCreate):
        query = {"name": data.name, "deletedAt": None}
        if hasattr(data, 'companyId') and data.companyId:
            query["companyId"] = data.companyId
            parent = await self.db["companies"].find_one({"_id": ObjectId(data.companyId), "deletedAt": None})
            if not parent:
                raise HTTPException(status_code=400, detail="Parent company not found or archived")
        if await self.collection.find_one(query):
            raise HTTPException(status_code=409, detail=f"Company with this name already exists")
            
    async def validate_update(self, id: str, data: CompanyUpdate):
        pass # Optional update validation
