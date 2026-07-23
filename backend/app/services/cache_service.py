"""Cache service with Redis and in-memory fallback."""
import json
import structlog
from typing import Any

logger = structlog.get_logger()


class CacheService:
    def __init__(self):
        self._redis = None
        self._memory_cache: dict[str, tuple[Any, float]] = {}

    async def _get_redis(self):
        if self._redis is None:
            try:
                import redis.asyncio as aioredis
                from app.config import settings
                self._redis = aioredis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=2,
                )
                await self._redis.ping()
                logger.info("redis_connected")
            except Exception as e:
                logger.warning("redis_unavailable", error=str(e))
                self._redis = False
        return self._redis if self._redis else None

    async def get(self, key: str) -> Any | None:
        redis = await self._get_redis()
        if redis:
            try:
                val = await redis.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.warning("redis_get_failed", key=key, error=str(e))

        import time
        if key in self._memory_cache:
            val, expiry = self._memory_cache[key]
            if time.time() < expiry:
                return val
            del self._memory_cache[key]
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 300):
        redis = await self._get_redis()
        if redis:
            try:
                await redis.setex(key, ttl_seconds, json.dumps(value, default=str))
                return
            except Exception as e:
                logger.warning("redis_set_failed", key=key, error=str(e))

        import time
        self._memory_cache[key] = (value, time.time() + ttl_seconds)

    async def delete(self, key: str):
        redis = await self._get_redis()
        if redis:
            try:
                await redis.delete(key)
            except Exception:
                pass
        self._memory_cache.pop(key, None)

    async def clear_pattern(self, pattern: str):
        redis = await self._get_redis()
        if redis:
            try:
                cursor = 0
                while True:
                    cursor, keys = await redis.scan(cursor=cursor, match=pattern)
                    if keys:
                        await redis.delete(*keys)
                    if cursor == 0:
                        break
            except Exception:
                pass
        self._memory_cache = {k: v for k, v in self._memory_cache.items()
                             if not k.startswith(pattern.replace("*", ""))}
