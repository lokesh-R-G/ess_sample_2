from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.organization.schemas.essl_machine import ESSLMachineCreate, ESSLMachineUpdate
from bson import ObjectId

class ESSLMachineValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["essl_machines"]
        
    async def validate_create(self, data: ESSLMachineCreate):
        query = {"serialNumber": data.serialNumber, "deletedAt": None}
        if await self.collection.find_one(query):
            raise HTTPException(status_code=409, detail="eSSL Machine with this serial number already exists")
            
    async def validate_update(self, id: str, data: ESSLMachineUpdate):
        if data.serialNumber is not None:
            query = {"serialNumber": data.serialNumber, "deletedAt": None, "_id": {"$ne": ObjectId(id)}}
            if await self.collection.find_one(query):
                raise HTTPException(status_code=409, detail="Another eSSL Machine with this serial number already exists")
