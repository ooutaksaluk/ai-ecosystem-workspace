# app/domains/training/router.py
from fastapi import APIRouter, Depends, HTTPException
import redis.asyncio as redis

from app.domains.training.schemas import TrainQueueRequest, TrainQueueResponse
from app.domains.training.service import TrainingService
from app.core.redis_client import get_redis_client   # dependency ที่มีอยู่แล้วในโปรเจกต์

router = APIRouter(prefix="/train", tags=["Training"])


def get_training_service(
    redis_client: redis.Redis = Depends(get_redis_client)
) -> TrainingService:
    return TrainingService(redis_client)


@router.post("/queue", response_model=TrainQueueResponse, status_code=201)
async def add_train_queue(
    req: TrainQueueRequest,
    service: TrainingService = Depends(get_training_service),
):
    """
    เพิ่ม training job เข้าคิว พร้อมกำหนดเวลาที่จะเริ่มเทรน
    (ตรงกับ 'Add train queue time' ใน diagram)
    """
    try:
        result = await service.enqueue_train_job(req)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/{job_id}")
async def get_train_status(
    job_id: str,
    service: TrainingService = Depends(get_training_service),
):
    job = await service.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job