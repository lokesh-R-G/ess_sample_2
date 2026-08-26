import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__)))
import asyncio
from app.db.mongo import get_database

async def check():
    db = get_database()
    sa_perms = await db.role_permissions.find({"roleId": "ROLE_SUPER_ADMIN"}).to_list(None)
    print("ROLE_SUPER_ADMIN perms count:", len(sa_perms))
    sa_perms2 = await db.role_permissions.find({"roleId": "super_admin"}).to_list(None)
    print("super_admin perms count:", len(sa_perms2))

asyncio.run(check())
