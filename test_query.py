import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv(dotenv_path='c:/ess/ess_sample_2/backend/.env')
client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('MONGODB_DB_NAME')]

async def check():
    emp_id = "1"
    month_str = "2026-10"
    
    await db.approvals.delete_many({"employeeId": emp_id, "remarks": "TEST_AUTO"})
    
    await db.approvals.insert_one({
        "employeeId": emp_id,
        "approvalType": "Permission",
        "status": "APPROVED",
        "remarks": "TEST_AUTO",
        "requestData": {
            "date": f"{month_str}-15",
            "fromTime": "10:00",
            "toTime": "12:00",
            "conversionLeaveType": "SL_TEST"
        },
        "createdAt": datetime.now(timezone.utc)
    })
    
    approvals = await db.approvals.find({
        "employeeId": emp_id,
        "approvalType": "Permission",
        "status": "APPROVED",
        "": [
            {"requestData.date": {"": f"^{month_str}"}},
            {"requestData.fromDate": {"": f"^{month_str}"}}
        ]
    }).to_list(length=None)
    
    print(f"Found {len(approvals)} approvals")
    for a in approvals:
        print(a.get("requestData"))
        
    await db.approvals.delete_many({"employeeId": emp_id, "remarks": "TEST_AUTO"})

asyncio.run(check())
