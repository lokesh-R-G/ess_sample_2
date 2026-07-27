from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.services.leave_balance_service import LeaveBalanceService
from app.leave.schemas.leave_balance import LeaveBalanceCreate, LeaveBalanceUpdate, LeaveBalanceResponse
from app.leave.models.leave_balance import LeaveBalanceModel

class LeaveBalanceController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveBalanceService(db)
        
    async def create(self, data: LeaveBalanceCreate, user_id: str) -> LeaveBalanceModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveBalanceModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveBalance not found")
        return doc
        
    async def update(self, id: str, data: LeaveBalanceUpdate, user_id: str) -> LeaveBalanceModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveBalance not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveBalance not found")
        return {"message": "LeaveBalance archived successfully"}
