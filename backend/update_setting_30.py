import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def update():
    db = AsyncIOMotorClient('mongodb://lokeshca2004_db_user:q7mutTirXPPe8AzC@ac-uj8llxh-shard-00-00.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-01.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-02.e5z9cjy.mongodb.net:27017/?ssl=true&authSource=admin&replicaSet=atlas-dztgx9-shard-0')['essl_production']
    await db.payroll_settings.update_one({'status': 'Active'}, {'$set': {'defaultSalaryCalculationMethod': 'Fixed 30 Days'}})
    print('Updated to Fixed 30 Days')

asyncio.run(update())
