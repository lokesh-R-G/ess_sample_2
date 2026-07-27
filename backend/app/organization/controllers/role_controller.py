from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.organization.services.role_service import RoleService
from app.organization.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.organization.models.role import RoleModel

class RoleController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = RoleService(db)
        
    async def create(self, data: RoleCreate, user_id: str) -> RoleModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> RoleModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="Role not found")
        return doc
        
    async def update(self, id: str, data: RoleUpdate, user_id: str) -> RoleModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Role not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Role not found")
        return {"message": "Role archived successfully"}
