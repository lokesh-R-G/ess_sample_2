import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient('mongodb+srv://lokeshca2004_db_user:maYiWdAooh5Qw7QM@cluster0.aehbv6j.mongodb.net/?retryWrites=true&w=majority')
    db = client.essl_production
    
    emp = await db.employees.find_one({'employeeCode': '5188'})
    print('Before:', emp.get('employment'))
    
    await db.employees.update_one(
        {'employeeCode': '5188'},
        {'$set': {
            'employment': {
                'companyId': '6a742dba89dd1899f87043b0',
                'branchId': '6a742e5f89dd1899f87043b4'
            }
        }}
    )
    
    emp_after = await db.employees.find_one({'employeeCode': '5188'})
    print('After:', emp_after.get('employment'))

asyncio.run(check())
