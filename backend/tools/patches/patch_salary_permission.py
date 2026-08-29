import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv

async def run_patch():
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "ess_db")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    print("Running patch_salary_permission...")
    now = datetime.utcnow()
    
    # 1. Ensure permission exists
    perm_doc = {
        "permissionId": "payroll.salary.manage",
        "name": "Manage Salary Configuration",
        "description": "Configure and finalize employee salary structure",
        "module": "payroll",
        "action": "salary.manage",
        "isActive": True,
        "version": 1,
        "createdAt": now,
        "updatedAt": now
    }
    
    perm = await db.permissions.find_one({"permissionId": "payroll.salary.manage"})
    if not perm:
        await db.permissions.insert_one(perm_doc)
        print(" -> Created permission: payroll.salary.manage")
    else:
        print(" -> Permission payroll.salary.manage already exists.")
        
    # 2. Add to admin and super_admin role_permissions
    for role_id in ["admin", "super_admin"]:
        role_perm = await db.role_permissions.find_one({
            "roleId": role_id, 
            "permissionId": "payroll.salary.manage"
        })
        if not role_perm:
            # We need to get the scope for this role
            role = await db.roles.find_one({"roleId": role_id})
            if role:
                scope = role.get("scope", "GLOBAL")
                await db.role_permissions.insert_one({
                    "roleId": role_id,
                    "permissionId": "payroll.salary.manage",
                    "scope": scope,
                    "isActive": True,
                    "createdAt": now
                })
                print(f" -> Added permission mapping to role: {role_id} with scope: {scope}")
            else:
                print(f" -> Role {role_id} not found, skipping mapping.")
        else:
            print(f" -> Role {role_id} already has payroll.salary.manage.")
            
    print("Patch completed safely.")

if __name__ == "__main__":
    asyncio.run(run_patch())
