import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

from app.core.security import decode_access_token
from app.db.mongo import get_database
from app.mail.repositories.mail_repository import MailRepository
from app.mail.services.mail_service import MailService
from app.mail.services.presence_service import PresenceService
from app.mail.services.realtime_service import RealtimeService

router = APIRouter(prefix="/v2/mail", tags=["Mailbox WebSocket"])

@router.websocket("/ws")
async def mail_websocket(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        payload = decode_access_token(token)
        emp_id = payload.get("sub") or payload.get("empId")
    except Exception:
        await websocket.close(code=1008, reason="Invalid token")
        return

    if not emp_id:
        await websocket.close(code=1008, reason="No employee ID in token")
        return

    user = await db.users.find_one({"empId": emp_id})
    if not user:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    employee_id = user.get("empId")
    if not employee_id:
        await websocket.close(code=1008, reason="No employee ID")
        return

    await websocket.accept()
    ws_id = str(uuid.uuid4())
    
    # Mark online
    await PresenceService.mark_online(employee_id, ws_id)
    
    repo = MailRepository(db)
    service = MailService(repo)

    # Subscribe to pub/sub
    pubsub = await RealtimeService.subscribe(employee_id)
    
    # Send pending offline messages
    pending = await service.handle_websocket_connect(employee_id)
    for p in pending:
        await websocket.send_json({
            "type": "message:new",
            "payload": p.model_dump(by_alias=False, mode="json")
        })

    async def listen_redis():
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_json(data)

    redis_task = asyncio.create_task(listen_redis())

    try:
        while True:
            data = await websocket.receive_json()
            # Handle client ACKs
            if data.get("type") == "message:ack":
                message_ids = data.get("messageIds", [])
                await service.handle_delivery_ack(message_ids, employee_id)
                # Client signals they received it, transition SENT -> DELIVERED
    except WebSocketDisconnect:
        pass
    finally:
        redis_task.cancel()
        await pubsub.unsubscribe()
        await PresenceService.mark_offline(employee_id, ws_id)
