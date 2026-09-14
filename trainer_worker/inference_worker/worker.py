import json
import os
import time

import mlflow
import redis
from mlflow.tracking import MlflowClient


redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=int(os.environ.get("REDIS_PORT", "6379")),
    decode_responses=True,
)
RESULT_PREFIX = "inference:result:"
JOB_PREFIX = "inference:job:"
RESULT_TTL_SECONDS = 3600


def resolve_model_uri(model_name: str, model_version: str) -> str:
    if model_version != "latest":
        return f"models:/{model_name}/{model_version}"
    versions = MlflowClient().get_latest_versions(model_name, stages=["None"])
    if not versions:
        raise ValueError(f"No model version found for {model_name}")
    return f"models:/{model_name}/{versions[0].version}"


def run_inference(job: dict) -> dict:
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    model_uri = resolve_model_uri(job["model_name"], job.get("model_version", "latest"))
    pipeline = mlflow.transformers.load_model(model_uri)
    prediction = pipeline(job["text"])[0]
    return {
        "job_id": job["job_id"],
        "status": "done",
        "prediction": int(prediction["label"])
        if str(prediction["label"]).isdigit()
        else prediction["label"],
    }


while True:
    item = redis_client.blpop("inference_queue", timeout=5)
    if not item:
        continue

    _, payload = item
    job = json.loads(payload)
    redis_client.hset(f"{JOB_PREFIX}{job['job_id']}", mapping={"status": "running"})
    try:
        result = run_inference(job)
    except Exception as exc:
        result = {
            "job_id": job["job_id"],
            "status": "failed",
            "error": str(exc),
        }
    redis_client.hset(f"{JOB_PREFIX}{job['job_id']}", mapping=result)
    redis_client.setex(
        f"{RESULT_PREFIX}{job['job_id']}",
        RESULT_TTL_SECONDS,
        json.dumps(result),
    )
    time.sleep(0.01)
