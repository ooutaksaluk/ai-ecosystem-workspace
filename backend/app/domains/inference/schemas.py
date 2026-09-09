from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    model_name: str = Field(..., min_length=1)
    model_version: str = Field(default="latest")
    text: str = Field(..., min_length=1)


class InferenceResponse(BaseModel):
    job_id: str
    status: str
    prediction: int | str | None = None
    error: str | None = None
