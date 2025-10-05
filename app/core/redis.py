import redis.asyncio as redis
from app.core.config import settings


class RedisService:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        await self.redis.ping()

    async def disconnect(self):
        if self.redis:
            await self.redis.close()


redis_service = RedisService()


async def get_redis():
    if not redis_service.redis:
        await redis_service.connect()
    return redis_service.redis