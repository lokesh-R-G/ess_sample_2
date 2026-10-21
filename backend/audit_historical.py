import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def audit():
    uri = "mongodb+srv://lokeshca2004_db_user:q7mutTirXPPe8AzC@cluster0.e5z9cjy.mongodb.net/"
    client = AsyncIOMotorClient(uri)
    db = client["essl_production"]
    
    # We want to find attendance documents where:
    # status == "Leave"
    # lopHours == 0
    # Inside approvalSnapshot, there's a leave that is REJECTED and fullDay == True
    
    cursor = db.attendance.find({
        "status": "Leave",
        "lopHours": 0,
        "approvalSnapshot": {
            "$elemMatch": {
                "approvalType": "Leave",
                "status": "REJECTED",
                "fullDay": True
            }
        }
    })
    
    affected_records = []
    async for record in cursor:
        affected_records.append({
            "employeeId": record.get("employeeId"),
            "employeeCode": record.get("employeeCode", record.get("empId")),
            "date": record.get("date"),
            "approvalSnapshot": [a for a in record.get("approvalSnapshot", []) if a.get("status") == "REJECTED" and a.get("fullDay")]
        })
        
    print(f"Total affected records: {len(affected_records)}")
    for r in affected_records:
        print(f" - Date: {r['date']}, Employee: {r['employeeCode']}, Approvals: {r['approvalSnapshot']}")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(audit())
