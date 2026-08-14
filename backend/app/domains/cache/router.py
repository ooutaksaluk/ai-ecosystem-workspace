from fastapi import APIRouter
from app.domains.cache import service

router = APIRouter(prefix="/cache", tags=["cache"])


@router.get(
    "/ping",
    summary="ตรวจสอบการเชื่อมต่อ Redis",
    response_description="สถานะการเชื่อมต่อ Redis",
)
async def cache_ping():
    return await service.check_redis_connection()


@router.post(
    "/set",
    summary="เก็บค่าลง Redis",
)
async def cache_set(key: str, value: str):
    return await service.set_value(key, value)


@router.get(
    "/get/{key}",
    summary="ดึงค่าจาก Redis ตาม key",
)
async def cache_get(key: str):
    return await service.get_value(key)