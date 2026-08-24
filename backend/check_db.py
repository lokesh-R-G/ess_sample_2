import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__)))
import asyncio
from app.db.mongo import get_database

async def check():
    db = get_database()
    sa_perms = await db.role_permissions.find({"roleId": "super_admin"}).to_list(None)
    for p in sa_perms:
        if p["permissionId"] == "attendance.read":
            print("super_admin attendance.read scope:", p["scope"])

    user = await db.users.find_one({"role": "Super Admin"})
    if user:
        print("Super Admin user:", user.get("roleId"), user.get("empId"), user.get("role"))
    else:
        print("No Super Admin user found.")

asyncio.run(check())
