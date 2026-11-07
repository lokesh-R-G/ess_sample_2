import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URI = "mongodb://lokeshca2004_db_user:q7mutTirXPPe8AzC@ac-uj8llxh-shard-00-00.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-01.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-02.e5z9cjy.mongodb.net:27017/?ssl=true&authSource=admin&replicaSet=atlas-dztgx9-shard-0"
DB_NAME = "essl_production"

async def check():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    with_reporting = await db.employee_employment_histories.count_documents({"reportingManagerEmployeeId": {"$exists": True}})
    with_manager = await db.employee_employment_histories.count_documents({"managerId": {"$exists": True}})
    
    print(f"reportingManagerEmployeeId count: {with_reporting}")
    print(f"managerId count: {with_manager}")
    
    # Also dump one record that has it
    doc = await db.employee_employment_histories.find_one({"reportingManagerEmployeeId": {"$exists": True}})
    print("Example doc:", doc)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check())
