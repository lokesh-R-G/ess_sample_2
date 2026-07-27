from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.employee.models.employee_document import EmployeeDocumentModel

class EmployeeDocumentRepository(BaseRepository[EmployeeDocumentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'employee_documents', EmployeeDocumentModel)
