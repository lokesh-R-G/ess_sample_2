from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional, Tuple
from datetime import datetime

from app.mail.models.conversation import ConversationModel
from app.mail.models.message import MessageModel

class MailRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.conversations = self.db["conversations"]
        self.messages = self.db["messages"]

    async def get_or_create_direct_conversation(self, employee_id_1: str, employee_id_2: str) -> ConversationModel:
        participants = sorted([employee_id_1, employee_id_2])
        query = {
            "type": "DIRECT",
            "participants": participants
        }
        conv = await self.conversations.find_one(query)
        if conv:
            conv["_id"] = str(conv["_id"])
            return ConversationModel(**conv)

        new_conv = ConversationModel(
            type="DIRECT",
            participants=participants
        )
        doc = new_conv.model_dump(by_alias=True, exclude_none=True)
        result = await self.conversations.insert_one(doc)
        new_conv.id = str(result.inserted_id)
        return new_conv

    async def get_conversation(self, conversation_id: str, participant_id: Optional[str] = None) -> Optional[ConversationModel]:
        if not ObjectId.is_valid(conversation_id):
            return None
        query = {"_id": ObjectId(conversation_id)}
        if participant_id:
            query["participants"] = participant_id
        
        doc = await self.conversations.find_one(query)
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return ConversationModel(**doc)

    async def get_user_conversations(self, employee_id: str) -> List[ConversationModel]:
        cursor = self.conversations.find({"participants": employee_id}).sort("lastMessageAt", -1)
        convs = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            convs.append(ConversationModel(**doc))
        return convs

    async def create_message(self, message: MessageModel) -> Tuple[MessageModel, bool]:
        # Idempotency check
        existing = await self.messages.find_one({
            "clientMessageId": message.clientMessageId,
            "senderEmployeeId": message.senderEmployeeId
        })
        if existing:
            existing["_id"] = str(existing["_id"])
            return MessageModel(**existing), False # False means not newly created

        doc = message.model_dump(by_alias=True, exclude_none=True)
        result = await self.messages.insert_one(doc)
        message.id = str(result.inserted_id)

        # Update conversation lastMessageAt
        await self.conversations.update_one(
            {"_id": ObjectId(message.conversationId)},
            {"$set": {"lastMessageAt": message.createdAt, "updatedAt": message.createdAt}}
        )

        return message, True

    async def get_conversation_messages(self, conversation_id: str, limit: int = 50, skip: int = 0) -> List[MessageModel]:
        cursor = self.messages.find({"conversationId": conversation_id}).sort("createdAt", -1).skip(skip).limit(limit)
        msgs = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            msgs.append(MessageModel(**doc))
        msgs.reverse() # chronological order
        return msgs

    async def get_undelivered_messages(self, receiver_id: str) -> List[MessageModel]:
        cursor = self.messages.find({
            "receiverEmployeeId": receiver_id,
            "status": "SENT"
        }).sort("createdAt", 1)
        msgs = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            msgs.append(MessageModel(**doc))
        return msgs

    async def mark_messages_delivered(self, message_ids: List[str]):
        valid_ids = [ObjectId(mid) for mid in message_ids if ObjectId.is_valid(mid)]
        if not valid_ids:
            return
        await self.messages.update_many(
            {"_id": {"$in": valid_ids}, "status": "SENT"},
            {"$set": {"status": "DELIVERED", "deliveredAt": datetime.utcnow()}}
        )

    async def mark_conversation_read(self, conversation_id: str, receiver_id: str):
        if not ObjectId.is_valid(conversation_id):
            return
        await self.messages.update_many(
            {
                "conversationId": conversation_id,
                "receiverEmployeeId": receiver_id,
                "status": {"$in": ["SENT", "DELIVERED"]}
            },
            {"$set": {"status": "READ", "readAt": datetime.utcnow()}}
        )

    async def count_unread_messages(self, receiver_id: str) -> int:
        return await self.messages.count_documents({
            "receiverEmployeeId": receiver_id,
            "status": {"$in": ["SENT", "DELIVERED"]}
        })
