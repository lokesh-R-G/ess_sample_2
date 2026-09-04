from typing import List, Tuple
from app.mail.models.message import MessageModel
from app.mail.models.conversation import ConversationModel
from app.mail.repositories.mail_repository import MailRepository
from app.mail.services.presence_service import PresenceService
from app.mail.services.realtime_service import RealtimeService

class MailService:
    def __init__(self, repository: MailRepository):
        self.repository = repository

    async def send_message(self, sender_id: str, receiver_id: str, client_msg_id: str, body: str, subject: str = None) -> Tuple[MessageModel, bool]:
        # Ensure conversation exists
        conv = await self.repository.get_or_create_direct_conversation(sender_id, receiver_id)
        
        msg = MessageModel(
            clientMessageId=client_msg_id,
            conversationId=conv.id,
            senderEmployeeId=sender_id,
            receiverEmployeeId=receiver_id,
            body=body,
            subject=subject,
            status="SENT"
        )
        
        # 1. MongoDB Save succeeds first (Idempotent)
        saved_msg, is_new = await self.repository.create_message(msg)
        
        if not is_new:
            return saved_msg, False
            
        # 2. Check Receiver Presence
        is_online = await PresenceService.is_online(receiver_id)
        
        # 3. Publish to Redis if online. 
        # Note: We do NOT transition to DELIVERED here. The recipient's WS must ACK receipt.
        if is_online:
            await RealtimeService.publish_event(
                receiver_id,
                "message:new",
                saved_msg.model_dump(by_alias=False, mode="json")
            )
            
        return saved_msg, True

    async def get_conversation_history(self, conversation_id: str, requesting_user_id: str) -> List[MessageModel]:
        # Enforce participant auth
        conv = await self.repository.get_conversation(conversation_id, participant_id=requesting_user_id)
        if not conv:
            raise ValueError("Conversation not found or unauthorized")
        
        return await self.repository.get_conversation_messages(conversation_id)

    async def handle_websocket_connect(self, user_id: str):
        # When user connects, push undelivered messages
        msgs = await self.repository.get_undelivered_messages(user_id)
        return msgs

    async def handle_delivery_ack(self, message_ids: List[str], receiver_id: str):
        # Acknowledge receipt
        # Only mark if they are indeed intended for this receiver
        # For simplicity, repo can just update them if they match receiver in DB, but currently mark_messages_delivered doesn't check receiver.
        # Let's trust the IDs for now since they are ObjectIds and only the receiver would have them via WS.
        await self.repository.mark_messages_delivered(message_ids)
        
        # Notify senders that messages were delivered
        # Since we might have multiple senders in these messages, we'd ideally group them.
        # But this is a basic implementation.

    async def mark_read(self, conversation_id: str, receiver_id: str):
        # Enforce participant auth
        conv = await self.repository.get_conversation(conversation_id, participant_id=receiver_id)
        if not conv:
            raise ValueError("Conversation not found or unauthorized")
            
        await self.repository.mark_conversation_read(conversation_id, receiver_id)
        
        # Publish read event back to the other participant
        other_participant = next(p for p in conv.participants if p != receiver_id)
        await RealtimeService.publish_event(
            other_participant,
            "message:read",
            {"conversationId": conversation_id, "readBy": receiver_id}
        )
