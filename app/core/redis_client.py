import asyncio
import logging
from typing import Optional
import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger("condigence.redis")


class RedisManager:
    redis: Optional[aioredis.Redis] = None
    is_connected: bool = False

    async def connect(self):
        try:
            logger.info(f"Connecting to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}...")
            self.redis = aioredis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD or None,
                decode_responses=True,
                socket_connect_timeout=0.8,
                socket_timeout=0.8
            )
            # Fast ping with 1s timeout
            await asyncio.wait_for(self.redis.ping(), timeout=1.0)
            self.is_connected = True
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            self.is_connected = False
            logger.warning(
                f"Redis connection offline ({type(e).__name__}). Running with local in-memory fallback."
            )

    async def disconnect(self):
        if self.redis:
            logger.info("Closing Redis connection...")
            await self.redis.aclose()
            self.is_connected = False

    async def get(self, key: str) -> Optional[str]:
        if self.is_connected and self.redis:
            try:
                return await self.redis.get(key)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        return None

    async def set(self, key: str, value: str, expire: int = 3600):
        if self.is_connected and self.redis:
            try:
                await self.redis.set(key, value, ex=expire)
            except Exception as e:
                logger.error(f"Redis set error: {e}")

    async def acquire_lock(self, lock_name: str, timeout: int = 10) -> bool:
        if self.is_connected and self.redis:
            try:
                acquired = await self.redis.set(f"lock:{lock_name}", "locked", nx=True, ex=timeout)
                return bool(acquired)
            except Exception as e:
                logger.error(f"Redis lock error: {e}")
        return True


redis_manager = RedisManager()
