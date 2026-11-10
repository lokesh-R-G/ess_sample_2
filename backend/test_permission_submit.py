import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.approval.services.approval_service import ApprovalService
from app.approval.schemas.approval import ApprovalSubmit

MONGODB_URI = "mongodb://lokeshca2004_db_user:q7mutTirXPPe8AzC@ac-uj8llxh-shard-00-00.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-01.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-02.e5z9cjy.mongodb.net:27017/?ssl=true&authSource=admin&replicaSet=atlas-dztgx9-shard-0"
DB_NAME = "essl_production"

async def test_submit():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    service = ApprovalService(db)
    
    # "1" is the employeeId. The manager is the same in the DB (self-reported or assigned to 6a9169127ab63c8399399515 which is employeeId "1")
    data = ApprovalSubmit(
        employeeId="1",
        approvalType="Miss Punch",
        requestData={"date": "2026-09-18"},
        remarks="Test permission fix"
    )
    
    try:
        model = await service.submit_request(data)
        print("Success!")
        print(model.model_dump_json(indent=2))
    except Exception as e:
        print(f"Failed: {e}")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(test_submit())
