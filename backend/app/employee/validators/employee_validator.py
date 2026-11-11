from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employee import EmployeeCreate, EmployeeUpdate
from bson import ObjectId

class EmployeeValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employees"]
        
    async def validate_create(self, data: EmployeeCreate):
        if data.machineId is not None:
            raw_mid = data.machineId.strip() if isinstance(data.machineId, str) else str(data.machineId).strip()
            if raw_mid:
                existing = await self.collection.find_one({
                    "machineId": raw_mid,
                    "deletedAt": None
                })
                if existing:
                    raise HTTPException(
                        status_code=409,
                        detail=f"Machine ID '{raw_mid}' is already assigned to employee {existing.get('employeeCode') or existing.get('employeeId')} ({existing.get('status')})."
                    )
            
    async def validate_update(self, id: str, data: EmployeeUpdate):
        if data.machineId is not None:
            raw_mid = data.machineId.strip() if isinstance(data.machineId, str) else str(data.machineId).strip()
            if raw_mid:
                query: dict = {
                    "machineId": raw_mid,
                    "deletedAt": None
                }
                # Exclude self by employeeId or _id
                or_clause = [{"employeeId": id}]
                if ObjectId.is_valid(id):
                    or_clause.append({"_id": ObjectId(id)})
                query["$nor"] = or_clause

                existing = await self.collection.find_one(query)
                if existing:
                    raise HTTPException(
                        status_code=409,
                        detail=f"Machine ID '{raw_mid}' is already assigned to employee {existing.get('employeeCode') or existing.get('employeeId')} ({existing.get('status')})."
                    ) 
