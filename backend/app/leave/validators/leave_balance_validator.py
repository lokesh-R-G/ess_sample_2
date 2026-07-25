from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_balance import LeaveBalanceCreate, LeaveBalanceUpdate

class LeaveBalanceValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_balances"]
        
    async def validate_create(self, data: LeaveBalanceCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveBalanceUpdate):
        pass 
