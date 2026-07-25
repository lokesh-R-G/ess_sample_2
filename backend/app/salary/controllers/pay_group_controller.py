from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.pay_group_service import PayGroupService
from ..schemas.pay_group import PayGroupCreate, PayGroupUpdate, PayGroupResponse
from ..models.pay_group import PayGroupModel

class PayGroupController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = PayGroupService(db)
        
    async def create(self, data: PayGroupCreate, user_id: str) -> PayGroupModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> PayGroupModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="PayGroup not found")
        return doc
        
    async def update(self, id: str, data: PayGroupUpdate, user_id: str) -> PayGroupModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="PayGroup not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="PayGroup not found")
        return {"message": "PayGroup archived successfully"}
