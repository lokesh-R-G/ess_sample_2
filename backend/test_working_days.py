import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    db = AsyncIOMotorClient('mongodb://lokeshca2004_db_user:q7mutTirXPPe8AzC@ac-uj8llxh-shard-00-00.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-01.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-02.e5z9cjy.mongodb.net:27017/?ssl=true&authSource=admin&replicaSet=atlas-dztgx9-shard-0')['essl_production']
    count = await db.attendance.count_documents({'employeeId': '1', 'date': {'$regex': '^2026-08'}})
    print('Aug 2026 attendance records for Emp 1:', count)
    
    # Check if there is any global config for payroll calculation settings
    print("Checking payroll configurations...")
    configs = await db.payroll_configs.find().to_list(None)
    for c in configs:
        print("global payroll config:", c)
        
    emp_configs = await db.employee_payroll_configs.find({'employeeId': '1'}).to_list(None)
    for c in emp_configs:
        print("emp payroll config:", c)

asyncio.run(check())
