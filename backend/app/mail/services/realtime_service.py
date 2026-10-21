import json
import logging
logger = logging.getLogger(__name__)
import asyncio
from app.core.redis import RedisManager

class RealtimeService:
    @staticmethod
    async def publish_event(receiver_employee_id: str, event_type: str, payload: dict):
        client = RedisManager.get_client()
        channel = f"mail:user:{receiver_employee_id}"
        message = {
            "type": event_type,
            "payload": payload
        }
        await client.publish(channel, json.dumps(message))

    @staticmethod
    async def subscribe(employee_id: str):
        client = RedisManager.get_client()
        pubsub = client.pubsub()
        channel = f"mail:user:{employee_id}"
        await pubsub.subscribe(channel)
        return pubsub
