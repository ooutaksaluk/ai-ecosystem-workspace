from fastapi import FastAPI
from app.domains.labeling.router import router as labeling_router
from app.core.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="AI Ecosystem API", version="1.0.0")

app.include_router(labeling_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("AI Ecosystem API เริ่มทำงานแล้ว")

@app.get("/health")
def health_check():
    return {"status": "ok"}