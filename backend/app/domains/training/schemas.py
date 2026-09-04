# app/domains/training/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class TrainQueueRequest(BaseModel):
    dataset_name: str = Field(..., example="conll2003")
    model_name: str = Field(..., example="bert-base-uncased")
    scheduled_time: datetime = Field(
        ..., 
        description="เวลาที่ต้องการให้เริ่มเทรน (ISO format)",
        example="2026-09-05T09:00:00"
    )
    epochs: int = Field(default=3, ge=1, le=100)
    batch_size: int = Field(default=16, ge=1)
    learning_rate: float = Field(default=5e-5)


class TrainQueueResponse(BaseModel):
    job_id: str
    status: JobStatus
    scheduled_time: datetime
    created_at: datetime