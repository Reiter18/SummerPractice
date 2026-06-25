import redis.asyncio as redis
import json
from typing import Optional, Any
from app.config import settings


class RedisCache:

    _client: Optional[redis.Redis] = None

    @classmethod
    async def get_client(cls) -> redis.Redis:
        if cls._client is None:
            cls._client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                max_connections=10
            )
        return cls._client

    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        client = await cls.get_client()
        data = await client.get(key)
        if data:
            return json.loads(data)
        return None

    @classmethod
    async def set(cls, key: str, value: Any, ttl: int = None) -> None:
        client = await cls.get_client()
        ttl = ttl or settings.cache_ttl_seconds
        await client.setex(key, ttl, json.dumps(value, default=str))

    @classmethod
    async def delete(cls, key: str) -> None:
        client = await cls.get_client()
        await client.delete(key)

    @classmethod
    async def clear(cls) -> None:
        client = await cls.get_client()
        await client.flushdb()


async def get_redis() -> redis.Redis:
    return await RedisCache.get_client()