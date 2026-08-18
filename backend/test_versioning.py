import asyncio
import os
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from app.attendance_policy.repositories.leave_policy_repository import LeavePolicyRepository
from app.attendance_policy.schemas.leave_policy import LeavePolicyCreate, LeaveTypeConfigSchema
from app.api.routes.leave_policy_v2 import create_policy
from fastapi import Depends

async def run_test():
    load_dotenv()
    db_client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = db_client[os.getenv('MONGODB_DB_NAME')]
    
    # 1. Create a dummy data for policy
    data = LeavePolicyCreate(
        policyCode="TEST_VERSIONING",
        name="Test Versioning Policy",
        effectiveFrom=datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc),
        leaveTypes=[
            LeaveTypeConfigSchema(
                code="SL",
                name="Sick Leave",
                annualEntitlement=12.0
            )
        ]
    )
    
    class MockUser:
        def get(self, key): return "test_user"
        
    try:
        # 1. First version
        res1 = await create_policy(data=data, current_user=MockUser())
        print(f"Created V1: version={res1.version}, eff_to={res1.effectiveTo}")
        
        # 2. Second version
        data2 = LeavePolicyCreate(
            policyCode="TEST_VERSIONING",
            name="Test Versioning Policy V2",
            effectiveFrom=datetime.datetime(2026, 6, 1, tzinfo=datetime.timezone.utc),
            leaveTypes=[
                LeaveTypeConfigSchema(
                    code="SL",
                    name="Sick Leave",
                    annualEntitlement=15.0
                )
            ]
        )
        res2 = await create_policy(data=data2, current_user=MockUser())
        print(f"Created V2: version={res2.version}, eff_to={res2.effectiveTo}")
        
        # 3. Check V1 again in DB
        v1_doc = await db.leave_policies.find_one({"policyCode": "TEST_VERSIONING", "version": 1})
        print(f"V1 now: isCurrent={v1_doc.get('isCurrent')}, eff_to={v1_doc.get('effectiveTo')}")
        
        # cleanup
        await db.leave_policies.delete_many({"policyCode": "TEST_VERSIONING"})
        
    except Exception as e:
        print("Error:", e)
        
    db_client.close()

if __name__ == "__main__":
    asyncio.run(run_test())
