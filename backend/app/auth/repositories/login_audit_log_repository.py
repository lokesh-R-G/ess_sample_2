from motor.motor_asyncio import AsyncIOMotorDatabase
from app.auth.repositories.base_repository import BaseRepository
from app.auth.models.login_audit_log import LoginAuditLogModel

class LoginAuditLogRepository(BaseRepository[LoginAuditLogModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'login_audit_logs', LoginAuditLogModel)
