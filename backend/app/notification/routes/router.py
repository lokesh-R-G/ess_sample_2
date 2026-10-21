from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional

from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.notification.services.notification_service import NotificationService
from app.notification.models.notification import NotificationModel

router = APIRouter(tags=["Notification Engine"])

@router.get("")

async def get_notifications(
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    recipient_id = current_user.get("employeeId")
    if not recipient_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    service = NotificationService(db)
    notifications = await service.get_notifications(recipient_id, limit, skip)
    return [n.model_dump(by_alias=False) for n in notifications]

@router.get("/unread-count")
async def get_unread_count(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    recipient_id = current_user.get("employeeId")
    if not recipient_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    service = NotificationService(db)
    count = await service.get_unread_count(recipient_id)
    return {"unreadCount": count}

@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    recipient_id = current_user.get("employeeId")
    if not recipient_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    service = NotificationService(db)
    success = await service.mark_as_read(notification_id, recipient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found or could not be updated")
    return {"status": "success"}

@router.patch("/read-all")
async def mark_all_as_read(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    recipient_id = current_user.get("employeeId")
    if not recipient_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    service = NotificationService(db)
    modified_count = await service.mark_all_as_read(recipient_id)
    return {"status": "success", "modified_count": modified_count}
