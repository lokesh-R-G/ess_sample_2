from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.organization.repositories.essl_machine_repository import ESSLMachineRepository
from app.organization.validators.essl_machine_validator import ESSLMachineValidator
from app.organization.schemas.essl_machine import ESSLMachineCreate, ESSLMachineUpdate
from app.organization.models.essl_machine import ESSLMachineModel

class ESSLMachineService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = ESSLMachineRepository(db)
        self.validator = ESSLMachineValidator(db)
        
    async def create(self, data: ESSLMachineCreate, user_id: str = None) -> ESSLMachineModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name", "serialNumber"])
        
    async def get_by_id(self, id: str) -> Optional[ESSLMachineModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: ESSLMachineUpdate, user_id: str = None) -> Optional[ESSLMachineModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        # Check if any branch is using this essl machine
        has_branches = await self.db["branchs"].find_one({"esslMachineId": id, "deletedAt": None})
        if has_branches:
            raise HTTPException(status_code=409, detail="Cannot archive eSSL Machine assigned to active Branches")
            
        return await self.repo.soft_delete(id, user_id)
