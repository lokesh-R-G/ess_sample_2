from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.schemas.salary_grade import SalaryGradeCreate, SalaryGradeUpdate

class SalaryGradeValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["salary_grades"]
        
    async def validate_create(self, data: SalaryGradeCreate):
        pass
            
    async def validate_update(self, id: str, data: SalaryGradeUpdate):
        pass 
