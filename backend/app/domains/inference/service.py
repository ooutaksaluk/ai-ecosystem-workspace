import json
import uuid

import redis.asyncio as redis

from app.domains.inference.schemas import InferenceRequest


RESULT_PREFIX = "inference:result:"
JOB_PREFIX = "inference:job:"


class InferenceService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def enqueue(self, request: InferenceRequest) -> tuple[str, dict]:
        request_id = str(uuid.uuid4())
        payload = {
            "job_id": request_id,
            "model_name": request.model_name,
            "model_version": request.model_version,
            "text": request.text,
        }
        await self.redis.hset(
            f"{JOB_PREFIX}{request_id}",
            mapping={**payload, "status": "queued"},
        )
        await self.redis.rpush("inference_queue", json.dumps(payload))
        return request_id, payload

    async def get_completed_result(self, request_id: str) -> dict | None:
        result = await self.redis.get(f"{RESULT_PREFIX}{request_id}")
        return json.loads(result) if result else None

    async def get_status(self, request_id: str) -> dict | None:
        result = await self.get_completed_result(request_id)
        if result:
            return result
        job = await self.redis.hgetall(f"{JOB_PREFIX}{request_id}")
        return job if job else None
