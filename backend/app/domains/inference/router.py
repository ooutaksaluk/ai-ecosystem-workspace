import asyncio

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException

from app.core.cache import get_redis_client
from app.domains.inference.schemas import InferenceRequest, InferenceResponse
from app.domains.inference.service import InferenceService


router = APIRouter(prefix="/inference", tags=["Inference"])


def get_inference_service(
    redis_client: redis.Redis = Depends(get_redis_client),
) -> InferenceService:
    return InferenceService(redis_client)


@router.post("/predict", response_model=InferenceResponse, status_code=202)
@router.post("", response_model=InferenceResponse, status_code=202)
async def predict(
    request: InferenceRequest,
    service: InferenceService = Depends(get_inference_service),
):
    request_id, _ = await service.enqueue(request)
    for _ in range(50):
        result = await service.get_completed_result(request_id)
        if result:
            return InferenceResponse(**result)
        await asyncio.sleep(0.1)
    return InferenceResponse(job_id=request_id, status="queued")


@router.get("/predict/{request_id}", response_model=InferenceResponse)
@router.get("/{request_id}", response_model=InferenceResponse)
async def get_prediction(
    request_id: str,
    service: InferenceService = Depends(get_inference_service),
):
    result = await service.get_status(request_id)
    if not result:
        raise HTTPException(status_code=404, detail="Inference result not found")
    return InferenceResponse(**result)
