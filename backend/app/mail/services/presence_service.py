from app.core.redis import RedisManager

class PresenceService:
    @staticmethod
    async def mark_online(employee_id: str, ws_id: str):
        client = RedisManager.get_client()
        key = f"presence:{employee_id}"
        await client.sadd(key, ws_id)
        # expire after 24h to clean up stale sessions if disconnect fails
        await client.expire(key, 86400)

    @staticmethod
    async def mark_offline(employee_id: str, ws_id: str):
        client = RedisManager.get_client()
        key = f"presence:{employee_id}"
        await client.srem(key, ws_id)
        
    @staticmethod
    async def is_online(employee_id: str) -> bool:
        client = RedisManager.get_client()
        key = f"presence:{employee_id}"
        count = await client.scard(key)
        return count > 0
