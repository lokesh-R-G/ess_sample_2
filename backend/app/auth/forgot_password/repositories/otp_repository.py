from motor.motor_asyncio import AsyncIOMotorDatabase
from app.auth.forgot_password.repositories.base_repository import BaseRepository
from app.auth.forgot_password.models.otp import PasswordResetOtpModel
from datetime import datetime, timezone
import pymongo

class OtpRepository(BaseRepository[PasswordResetOtpModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "password_reset_otps", PasswordResetOtpModel)
        self.collection.create_index("expiresAt", expireAfterSeconds=0)

    async def invalidate_previous_otps(self, employee_id: str):
        now = datetime.now(timezone.utc)
        await self.collection.update_many(
            {"employeeId": employee_id, "used": False, "verified": False},
            {"$set": {"used": True, "updatedAt": now}}
        )

    async def find_active_otp(self, employee_id: str) -> PasswordResetOtpModel | None:
        now = datetime.now(timezone.utc)
        doc = await self.collection.find_one(
            {"employeeId": employee_id, "used": False, "verified": False, "expiresAt": {"$gt": now}},
            sort=[("createdAt", pymongo.DESCENDING)]
        )
        if doc:
            return PasswordResetOtpModel(**self._prepare_doc(doc))
        return None

    async def increment_attempts(self, otp_id: str):
        await self.collection.update_one(
            {"_id": otp_id},
            {"$inc": {"attemptCount": 1}, "$set": {"updatedAt": datetime.now(timezone.utc)}}
        )

    async def mark_verified(self, otp_id: str):
        await self.collection.update_one(
            {"_id": otp_id},
            {"$set": {"verified": True, "updatedAt": datetime.now(timezone.utc)}}
        )

    async def mark_used(self, otp_id: str):
        await self.collection.update_one(
            {"_id": otp_id},
            {"$set": {"used": True, "updatedAt": datetime.now(timezone.utc)}}
        )

    async def count_recent_otps(self, employee_id: str, since: datetime) -> int:
        return await self.collection.count_documents(
            {"employeeId": employee_id, "createdAt": {"$gte": since}}
        )
