import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__)))
import asyncio
from app.db.mongo import get_database

async def check():
    db = get_database()
    roles = await db.role_permissions.distinct("roleId")
    print("Role IDs with permissions:", roles)

asyncio.run(check())
