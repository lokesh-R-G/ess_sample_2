from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from pydantic import BaseModel

from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.mail.repositories.mail_repository import MailRepository
from app.mail.services.mail_service import MailService
from app.mail.models.conversation import ConversationResponse
from app.mail.models.message import MessageModel

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Mailbox"])

class SendMessageRequest(BaseModel):
    receiverEmployeeId: str
    clientMessageId: str
    body: str
    subject: str = None

@router.post("/messages")
async def send_message(
    req: SendMessageRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    sender_id = current_user.get("employeeId")
    if not sender_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    repo = MailRepository(db)
    service = MailService(repo)
    
    msg, is_new = await service.send_message(
        sender_id=sender_id,
        receiver_id=req.receiverEmployeeId,
        client_msg_id=req.clientMessageId,
        body=req.body,
        subject=req.subject
    )
    
    return msg.model_dump(by_alias=False)

@router.get("/conversations")
async def get_conversations(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    sender_id = current_user.get("employeeId")
    repo = MailRepository(db)
    convs = await repo.get_user_conversations(sender_id)
    return [c.model_dump(by_alias=False) for c in convs]

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    sender_id = current_user.get("employeeId")
    repo = MailRepository(db)
    service = MailService(repo)
    try:
        msgs = await service.get_conversation_history(conversation_id, sender_id)
        return [m.model_dump(by_alias=False) for m in msgs]
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.patch("/conversations/{conversation_id}/read")
async def mark_conversation_read(
    conversation_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    sender_id = current_user.get("employeeId")
    repo = MailRepository(db)
    service = MailService(repo)
    try:
        await service.mark_read(conversation_id, sender_id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/unread-count")
async def get_unread_count(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    sender_id = current_user.get("employeeId")
    repo = MailRepository(db)
    count = await repo.count_unread_messages(sender_id)
    return {"unreadCount": count}
