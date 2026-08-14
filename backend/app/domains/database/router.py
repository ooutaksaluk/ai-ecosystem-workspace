from fastapi import APIRouter
from app.domains.database import service

router = APIRouter(prefix="/database", tags=["database"])


@router.get(
    "/health",
    summary="ตรวจสอบการเชื่อมต่อ PostgreSQL",
    response_description="สถานะการเชื่อมต่อฐานข้อมูล",
)
async def database_health():
    return await service.check_database_connection()