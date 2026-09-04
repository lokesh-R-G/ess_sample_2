import redis.asyncio as redis
from typing import Optional
from app.core.config import get_settings

class RedisManager:
    _pool: Optional[redis.ConnectionPool] = None
    _client: Optional[redis.Redis] = None

    @classmethod
    async def init(cls):
        settings = get_settings()
        cls._pool = redis.ConnectionPool.from_url(settings.redis_url, decode_responses=True)
        cls._client = redis.Redis(connection_pool=cls._pool)

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None
        if cls._pool:
            await cls._pool.disconnect()
            cls._pool = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        if not cls._client:
            raise RuntimeError("Redis not initialized")
        return cls._client
