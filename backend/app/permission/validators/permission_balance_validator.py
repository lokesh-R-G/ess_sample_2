from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.permission.schemas.permission_balance import PermissionBalanceCreate, PermissionBalanceUpdate

class PermissionBalanceValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["permission_balances"]
        
    async def validate_create(self, data: PermissionBalanceCreate):
        pass
            
    async def validate_update(self, id: str, data: PermissionBalanceUpdate):
        pass 
