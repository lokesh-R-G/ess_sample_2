from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_settings
from app.services.auth_service import create_provisioned_user, validate_employee_with_essl
from app.services.sync_service import sync_essl_logs


async def main() -> None:
    settings = get_settings()
    if not settings.mongo_uri:
        raise RuntimeError("MONGODB_URI is not configured")

    raw_users = os.getenv("BOOTSTRAP_USERS_JSON", "").strip()
    raw_emp_ids = os.getenv("BOOTSTRAP_EMP_IDS", "").strip()

    users: list[dict[str, str]]
    if raw_users:
        users = json.loads(raw_users)
    elif raw_emp_ids:
        users = [{"empId": emp_id.strip(), "role": "Employee"} for emp_id in raw_emp_ids.split(",") if emp_id.strip()]
    else:
        raise RuntimeError("Provide BOOTSTRAP_USERS_JSON or BOOTSTRAP_EMP_IDS")

    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]

    for user in users:
        if not await validate_employee_with_essl(user["empId"]):
            raise RuntimeError(f"Employee {user['empId']} is not present in eSSL")

        await create_provisioned_user(db, user["empId"], user.get("role", "Employee"))

    if users:
        await sync_essl_logs(db)

    print(f"Bootstrapped {len(users)} user(s)")


if __name__ == "__main__":
    asyncio.run(main())
