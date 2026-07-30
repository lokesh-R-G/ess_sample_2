from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.organization.services.essl_machine_service import ESSLMachineService
from app.organization.schemas.essl_machine import ESSLMachineCreate, ESSLMachineUpdate, ESSLMachineResponse
from app.organization.models.essl_machine import ESSLMachineModel

class ESSLMachineController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = ESSLMachineService(db)
        
    async def create(self, data: ESSLMachineCreate, user_id: str) -> ESSLMachineModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> ESSLMachineModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="eSSL Machine not found")
        return doc
        
    async def update(self, id: str, data: ESSLMachineUpdate, user_id: str) -> ESSLMachineModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="eSSL Machine not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="eSSL Machine not found")
        return {"message": "eSSL Machine archived successfully"}
