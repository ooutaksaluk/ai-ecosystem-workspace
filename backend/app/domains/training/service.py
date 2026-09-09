# app/domains/training/service.py
import json
import uuid
from datetime import datetime
import redis.asyncio as redis

from app.domains.training.schemas import (
    TrainQueueRequest, TrainQueueResponse, JobStatus
)

JOB_HASH_PREFIX = "job:"           # เก็บรายละเอียด job แต่ละอัน


class TrainingService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def enqueue_train_job(self, req: TrainQueueRequest) -> TrainQueueResponse:
        job_id = str(uuid.uuid4())
        created_at = datetime.utcnow()

        job_data = {
            "job_id": job_id,
            "dataset_name": req.dataset_name,
            "dataset_key": req.dataset_key,
            "model_name": req.model_name,
            "scheduled_time": req.scheduled_time.isoformat(),
            "epochs": req.epochs,
            "batch_size": req.batch_size,
            "learning_rate": req.learning_rate,
            "status": JobStatus.QUEUED.value,
            "created_at": created_at.isoformat(),
        }

        # 1. เก็บรายละเอียด job ไว้ใน Hash (key = job:<job_id>)
        await self.redis.hset(f"{JOB_HASH_PREFIX}{job_id}", mapping=job_data)

        # The worker consumes JSON jobs from this Redis list.
        await self.redis.rpush("train_queue", json.dumps(job_data))

        return TrainQueueResponse(
            job_id=job_id,
            status=JobStatus.QUEUED,
            scheduled_time=req.scheduled_time,
            created_at=created_at,
        )

    async def get_job_status(self, job_id: str) -> dict | None:
        data = await self.redis.hgetall(f"{JOB_HASH_PREFIX}{job_id}")
        return data if data else None