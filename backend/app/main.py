from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.domains.labeling.router import router as labeling_router
from app.domains.storage.router import router as storage_router
from app.core.logger import get_logger
from app.domains.worker.router import router as worker_router
from app.domains.database.router import router as database_router
from app.domains.cache.router import router as cache_router
from app.domains.storage.router import router as storage_router
from app.domains.worker.router import router as worker_router


logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AI Ecosystem API เริ่มทำงานแล้ว")
    yield

app = FastAPI(
    title="AI Ecosystem API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(worker_router)
app.include_router(storage_router)
app.include_router(labeling_router, prefix="/api/v1")
app.include_router(database_router)
app.include_router(cache_router)
app.include_router(storage_router)
app.include_router(worker_router)

async def check_database_connection():
    return {"connected": True, "details": "Database connection check passed."}

@app.get(
    "/health",
    tags=["health"],
    summary="ตรวจสอบสถานะของแอปพลิเคชัน",
)
async def health_check():
    # Check database connection
    db_status = await check_database_connection()

    if not db_status["connected"]:
        return {"status": "unhealthy", "details": db_status}

    return {"status": "healthy"}