from motor.motor_asyncio import AsyncIOMotorDatabase
from app.audit.repositories.base_repository import BaseRepository
from app.audit.models.audit_log import AuditLogModel

class AuditLogRepository(BaseRepository[AuditLogModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'audit_logs', AuditLogModel)
