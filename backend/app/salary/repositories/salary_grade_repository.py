from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.salary_grade import SalaryGradeModel

class SalaryGradeRepository(BaseRepository[SalaryGradeModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "salary_grades", SalaryGradeModel)
