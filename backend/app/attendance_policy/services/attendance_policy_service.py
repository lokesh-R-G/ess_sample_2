from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from app.attendance_policy.repositories.attendance_policy_repository import AttendancePolicyRepository
from app.attendance_policy.schemas.attendance_policy import AttendancePolicyCreate, AttendancePolicyUpdate

class AttendancePolicyService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = AttendancePolicyRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, policy_id: str) -> Optional[dict]:
        return await self.repo.get_by_id(policy_id)

    async def create(self, data: AttendancePolicyCreate, current_user_id: str) -> dict:
        exists = await self.repo.collection.find_one({"attendancePolicyCode": data.attendancePolicyCode, "deletedAt": None})
        if exists:
            raise ValueError(f"Attendance Policy with code {data.attendancePolicyCode} already exists.")
        return await self.repo.create(data.model_dump(exclude_unset=True), created_by=current_user_id)

    async def update(self, policy_id: str, data: AttendancePolicyUpdate, current_user_id: str) -> Optional[dict]:
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(policy_id, update_data, updated_by=current_user_id)

    async def delete(self, policy_id: str, current_user_id: str) -> bool:
        return await self.repo.soft_delete(policy_id, deleted_by=current_user_id)

    async def get_history(self, code: str) -> List[dict]:
        cursor = self.repo.collection.find({"attendancePolicyCode": code, "deletedAt": None}).sort("version", -1)
        return [self.repo._format_doc(doc) async for doc in cursor]
