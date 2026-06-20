from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends

from ...core.config import get_settings
from ...core.security import create_access_token
from ...db.mongo import get_database
from ...dependencies import get_current_user
from ...models import ChangePasswordRequest, LoginRequest, TokenResponse, UserResponse
from ...services.auth_service import authenticate_or_provision_user, change_password, serialize_user
from ...scheduler.scheduler import schedule_user_sync_now
from datetime import timedelta, timezone, datetime


router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    db = get_database()
    user = await authenticate_or_provision_user(db, payload.empId, payload.password)
    user_view = serialize_user(user)
    # If this is the user's first login, kick off a background sync for the last 90 days
    if user_view.get("firstLogin"):
        # mark processing; schedule background sync for last 90 days
        await db.users.update_one({"empId": user_view["empId"]}, {"$set": {"dataSyncStatus": "processing"}})
        from_date = datetime.now(timezone.utc) - timedelta(days=90)
        schedule_user_sync_now(user_view["empId"], from_date=from_date, to_date=None)
    token = create_access_token(
        {
            "empId": user_view["empId"],
            "role": user_view["role"],
            "firstLogin": user_view["firstLogin"],
        },
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes),
    )
    return TokenResponse(
        accessToken=token,
        empId=user_view["empId"],
        role=user_view["role"],
        firstLogin=user_view["firstLogin"],
        mustChangePassword=user_view["firstLogin"],
    )


@router.post("/change-password", response_model=UserResponse)
async def update_password(payload: ChangePasswordRequest, current_user=Depends(get_current_user)):
    db = get_database()
    updated = await change_password(db, current_user["empId"], payload.currentPassword, payload.newPassword)
    return UserResponse(empId=updated["empId"], role=updated.get("role", "Employee"), firstLogin=bool(updated.get("firstLogin", False)))


@router.get("/me", response_model=UserResponse)
async def me(current_user=Depends(get_current_user)):
    user_data = dict(current_user)
    if "_id" in user_data:
        del user_data["_id"]
    return UserResponse(**user_data)
