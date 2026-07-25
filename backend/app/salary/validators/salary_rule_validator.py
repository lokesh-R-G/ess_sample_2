from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.salary_rule import SalaryRuleCreate, SalaryRuleUpdate

class SalaryRuleValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["salary_rules"]
        
    async def validate_create(self, data: SalaryRuleCreate):
        pass
            
    async def validate_update(self, id: str, data: SalaryRuleUpdate):
        pass 
