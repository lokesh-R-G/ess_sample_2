import asyncio
from mongomock_motor import AsyncMongoMockClient

async def main():
    client = AsyncMongoMockClient()
    db = client.test_db
    await db.trip_allowance_policies.insert_one({
        "companyId": "compA",
        "policyCode": "TRIP_ALL_DEFAULT",
        "effectiveFrom": "2020-01-01",
        "effectiveTo": None,
        "isActive": True
    })
    
    date_str = "2023-01-01"
    query = {
        "companyId": "compA",
        "policyCode": "TRIP_ALL_DEFAULT",
        "isActive": True,
        "effectiveFrom": {"$lte": date_str},
        "$or": [{"effectiveTo": None}, {"effectiveTo": {"$gte": date_str}}]
    }
    
    docs = await db.trip_allowance_policies.find(query).to_list(None)
    print("Found docs:", docs)

asyncio.run(main())
