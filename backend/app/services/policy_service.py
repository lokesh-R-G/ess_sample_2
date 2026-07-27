from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import AttendancePolicy

async def get_attendance_policy(db: AsyncIOMotorDatabase) -> AttendancePolicy:
    policy_doc = await db.settings.find_one({"_id": "attendance_policy"})
    if not policy_doc:
        policy = AttendancePolicy()
        await db.settings.insert_one({"_id": "attendance_policy", **policy.model_dump()})
        return policy
    
    # Exclude _id when building model
    policy_data = {k: v for k, v in policy_doc.items() if k != "_id"}
    return AttendancePolicy(**policy_data)

async def update_attendance_policy(db: AsyncIOMotorDatabase, policy: AttendancePolicy) -> AttendancePolicy:
    await db.settings.update_one(
        {"_id": "attendance_policy"},
        {"$set": policy.model_dump()},
        upsert=True
    )
    return policy
