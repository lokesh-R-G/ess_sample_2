import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from app.attendance_policy.repositories.leave_policy_repository import LeavePolicyRepository
from app.attendance_policy.models.leave_policy import LeavePolicy

async def test_get_all():
    load_dotenv('../../backend/.env')
    db_client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = db_client[os.getenv('MONGODB_DB_NAME')]
    repo = LeavePolicyRepository(db)
    
    try:
        policies = await repo.get_all(skip=0, limit=10)
        import pprint
        pprint.pprint(policies)
    except Exception as e:
        print("Error:", e)
        
    db_client.close()

if __name__ == "__main__":
    asyncio.run(test_get_all())
