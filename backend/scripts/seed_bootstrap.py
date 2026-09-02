import asyncio
import os
import sys
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Ensure we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.security import hash_password
from app.permission.engine.seed_permissions import seed_permissions
from app.role.engine.seed_roles import seed_roles_and_mappings

async def main():
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    mongo_uri = os.environ.get("MONGODB_URI")
    db_name = os.environ.get("MONGODB_DB_NAME", "ess")

    if not mongo_uri:
        print("MONGODB_URI not set")
        sys.exit(1)

    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]

    print("Seeding permissions...")
    perm_result = await seed_permissions(db)
    print("Permissions seed result:", perm_result)

    print("Seeding roles and mappings...")
    role_result = await seed_roles_and_mappings(db)
    print("Roles seed result:", role_result)

    print("Bootstrapping canonical Super Admin identity...")
    now = datetime.now(timezone.utc)
    
    # 1. Ensure employee record exists
    emp_id = "5188"
    emp_code = "0001"
    password = "Admin@123"

    emp_doc = {
        "employeeId": emp_id,
        "employeeCode": emp_code,
        "firstName": "Super",
        "lastName": "Admin",
        "email": "super_admin@ess.local",
        "isActive": True,
        "createdAt": now,
        "updatedAt": now,
    }
    await db.employees.update_one(
        {"employeeId": emp_id},
        {"$set": emp_doc},
        upsert=True
    )

    # 2. Ensure user identity exists with canonical roleId
    user_doc = {
        "empId": emp_id,
        "roleId": "super_admin",
        "passwordHash": hash_password(password),
        "firstLogin": False,
        "isActive": True,
        "createdAt": now,
        "updatedAt": now,
    }
    
    # Clean up any old "role" field for this user if it exists
    await db.users.update_one(
        {"empId": emp_id},
        {"$unset": {"role": ""}}
    )
    
    res = await db.users.update_one(
        {"empId": emp_id},
        {"$set": user_doc},
        upsert=True
    )
    print(f"Super Admin user provisioned. Upsert: {res.upserted_id is not None}")
    
    print("Bootstrap complete. You can now login with employeeCode '0001' and password 'Admin@123'")

if __name__ == "__main__":
    asyncio.run(main())
