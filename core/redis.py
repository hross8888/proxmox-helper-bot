import redis.asyncio as redis

from core.settings import REDIS_URL

redis_client = redis.from_url(REDIS_URL)