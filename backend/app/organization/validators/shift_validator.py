from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.organization.schemas.shift import ShiftCreate, ShiftUpdate
from bson import ObjectId

class ShiftValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["shifts"]
        
    async def validate_create(self, data: ShiftCreate):
        query = {"shiftCode": data.shiftCode, "deletedAt": None}
        if await self.collection.find_one(query):
            raise HTTPException(status_code=409, detail=f"Shift with this shiftCode already exists")
            
        policy = await self.db["attendance_policies"].find_one({"_id": ObjectId(data.attendancePolicyId), "deletedAt": None})
        if not policy:
            raise HTTPException(status_code=400, detail="Attendance Policy not found or archived")
            
    async def validate_update(self, id: str, data: ShiftUpdate):
        pass # Optional update validation
