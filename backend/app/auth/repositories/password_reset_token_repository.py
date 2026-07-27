from motor.motor_asyncio import AsyncIOMotorDatabase
from app.auth.repositories.base_repository import BaseRepository
from app.auth.models.password_reset_token import PasswordResetTokenModel

class PasswordResetTokenRepository(BaseRepository[PasswordResetTokenModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'password_reset_tokens', PasswordResetTokenModel)
