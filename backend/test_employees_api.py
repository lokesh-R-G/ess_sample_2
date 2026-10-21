import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.employee.repositories.employee_repository import EmployeeRepository
import json

MONGODB_URI = "mongodb://lokeshca2004_db_user:q7mutTirXPPe8AzC@ac-uj8llxh-shard-00-00.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-01.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-02.e5z9cjy.mongodb.net:27017/?ssl=true&authSource=admin&replicaSet=atlas-dztgx9-shard-0"
DB_NAME = "essl_production"

async def test():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    repo = EmployeeRepository(db)
    
    result = await repo.get_all(skip=0, limit=100)
    
    print(f"Total: {result['total']}")
    
    for emp in result['data']:
        if emp.get("employeeCode") in ["5188", "5182", "1001"]:
            print(json.dumps(emp, indent=2))
            
    client.close()

if __name__ == "__main__":
    asyncio.run(test())
