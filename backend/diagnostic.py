import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys

async def diagnostic():
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient('mongodb+srv://lokeshca2004_db_user:maYiWdAooh5Qw7QM@cluster0.aehbv6j.mongodb.net/')
        db = client['essl_production']  # from .env
        
        print('--- 1 & 8. Checking users collection for Super Admin identities ---')
        users = await db.users.find({'role': {'$regex': 'super', '$options': 'i'}}).to_list(None)
        if not users:
            users = await db.users.find({'roleId': {'$regex': 'super', '$options': 'i'}}).to_list(None)
        
        for u in users:
            print(f"User empId: {u.get('empId')}, role: '{u.get('role')}', roleId: '{u.get('roleId')}'")
            
        print('\n--- 2 & 8. Checking roles collection ---')
        roles = await db.roles.find({'roleId': {'$regex': 'super', '$options': 'i'}}).to_list(None)
        for r in roles:
            print(f"Role: {r}")
            
        print('\n--- 3, 4, 6. Checking role_permissions collection for super_admin attendance.read ---')
        rp = await db.role_permissions.find({
            'roleId': {'$regex': 'super', '$options': 'i'},
            'permissionId': 'attendance.read'
        }).to_list(None)
        
        for p in rp:
            print(f"Mapping: {p}")
            
        print('\n--- 5. Checking permissions collection for attendance.read ---')
        perm = await db.permissions.find_one({'permissionId': 'attendance.read'})
        print(f"Permission: {perm}")
        
        # Check how many role_permissions total to see if seeding happened
        count = await db.role_permissions.count_documents({})
        print(f'\nTotal role_permissions in DB: {count}')
        
    except Exception as e:
        print(f'Error: {e}')
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(diagnostic())
