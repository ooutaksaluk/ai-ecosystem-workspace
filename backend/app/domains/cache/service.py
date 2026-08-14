from app.core.cache import get_redis_client


async def check_redis_connection() -> dict:
    client = get_redis_client()
    try:
        pong = await client.ping()
        return {"connected": pong}
    except Exception as e:
        return {"connected": False, "error": str(e)}


async def set_value(key: str, value: str) -> dict:
    client = get_redis_client()
    await client.set(key, value)
    return {"key": key, "value": value, "status": "set"}


async def get_value(key: str) -> dict:
    client = get_redis_client()
    value = await client.get(key)
    return {"key": key, "value": value}