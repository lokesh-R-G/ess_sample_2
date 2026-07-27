from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.organization.services.branch_service import BranchService
from app.organization.schemas.branch import BranchCreate, BranchUpdate, BranchResponse
from app.organization.models.branch import BranchModel

class BranchController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = BranchService(db)
        
    async def create(self, data: BranchCreate, user_id: str) -> BranchModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> BranchModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="Branch not found")
        return doc
        
    async def update(self, id: str, data: BranchUpdate, user_id: str) -> BranchModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Branch not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Branch not found")
        return {"message": "Branch archived successfully"}
