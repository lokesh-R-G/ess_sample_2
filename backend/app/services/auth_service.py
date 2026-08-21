from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.security import hash_password, verify_password
from app.services.sync_service import sync_essl_logs
import asyncio
from app.email_service.services.email_service import EmailService


settings = get_settings()


def serialize_user(user: dict) -> dict:
    return {
        "empId": user["empId"],
        "role": user.get("role", "Employee"),
        "roleId": user.get("roleId"),
        "firstLogin": bool(user.get("firstLogin", True)),
    }


async def authenticate_user(db, emp_id: str, password: str) -> dict:
    user = await db.users.find_one({"empId": emp_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    password_hash = user.get("passwordHash") or ""
    if not verify_password(password, password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return user


async def validate_employee_with_essl(emp_id: str) -> bool:
    try:
        client = build_essl_client()
    except RuntimeError:
        return False

    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(days=365)
    records = await asyncio.to_thread(client.fetch_transactions, from_date, to_date)
    return any(record.get("empId") == emp_id for record in records)


async def create_provisioned_user(db, emp_id: str, role: str = "Employee") -> dict:
    now = datetime.now(timezone.utc)
    document = {
        "empId": emp_id,
        "role": role,
        "passwordHash": create_default_password_hash(),
        "firstLogin": True,
        "isActive": True,
        "createdAt": now,
    }
    await db.users.update_one(
        {"empId": emp_id},
        {
            "$setOnInsert": document,
            "$set": {"updatedAt": now},
        },
        upsert=True,
    )
    created = await db.users.find_one({"empId": emp_id})
    return created or document


async def authenticate_or_provision_user(db, emp_id: str, password: str) -> dict:
    user = await db.users.find_one({"empId": emp_id})
    if user is None:
        if not await validate_employee_with_essl(emp_id):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        user = await create_provisioned_user(db, emp_id)
        # Do not perform a full sync here to avoid blocking login; scheduling of per-user sync
        # is handled by the login route or admin operations.

    password_hash = user.get("passwordHash") or ""
    if not verify_password(password, password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return user


async def change_password(db, emp_id: str, current_password: str, new_password: str) -> dict:
    user = await db.users.find_one({"empId": emp_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(current_password, user.get("passwordHash") or ""):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    new_hash = hash_password(new_password)
    await db.users.update_one(
        {"empId": emp_id},
        {
            "$set": {
                "passwordHash": new_hash,
                "firstLogin": False,
                "passwordUpdatedAt": datetime.now(timezone.utc),
            }
        },
    )
    updated = await db.users.find_one({"empId": emp_id})
    
    # Email Integration
    email_service = EmailService(db)
    
    employee_id = updated.get("employeeId") if updated else user.get("employeeId")
    if employee_id:
        from app.employee.services.email_resolver import get_employee_personal_email
        try:
            contact_email = await get_employee_personal_email(db, employee_id)
            context = {
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "time": datetime.now(timezone.utc).strftime("%H:%M:%S UTC"),
                "ip_address": "Security Context"
            }
            asyncio.create_task(email_service.send_password_changed_notification(recipient=contact_email, context=context))
        except ValueError as e:
            print(f"[AuthService] Cannot send password changed notification: {e}")
    
    return updated or user


def create_default_password_hash() -> str:
    return hash_password(settings.default_password)
