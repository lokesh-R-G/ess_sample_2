import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def check():
    db = AsyncIOMotorClient('mongodb://lokeshca2004_db_user:q7mutTirXPPe8AzC@ac-uj8llxh-shard-00-00.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-01.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-02.e5z9cjy.mongodb.net:27017/?ssl=true&authSource=admin&replicaSet=atlas-dztgx9-shard-0')['essl_production']
    
    print("\nCHECKING PAYROLL_SETTINGS:")
    settings = await db.payroll_settings.find().to_list(None)
    for s in settings:
        print(s)

asyncio.run(check())
