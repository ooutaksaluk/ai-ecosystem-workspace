import redis.asyncio as redis
from app.core.config import settings

# สร้าง connection pool เดียวใช้ร่วมกันทั้งแอป
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


def get_redis_client() -> redis.Redis:
    """Dependency สำหรับ inject เข้า router อื่น ๆ"""
    return redis.Redis(connection_pool=redis_pool)


async def check_redis_connection() -> bool:
    client = get_redis_client()
    try:
        return await client.ping()
    except Exception:
        return False