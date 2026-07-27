from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.schemas.salary_policy import SalaryPolicyCreate, SalaryPolicyUpdate

class SalaryPolicyValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["salary_policys"]
        
    async def validate_create(self, data: SalaryPolicyCreate):
        pass
            
    async def validate_update(self, id: str, data: SalaryPolicyUpdate):
        pass 
