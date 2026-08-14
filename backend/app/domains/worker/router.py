from fastapi import APIRouter, HTTPException
from rq.job import Job
from app.domains.worker.settings import task_queue, redis_conn
from app.domains.worker.tasks import process_uploaded_file

router = APIRouter(prefix="/worker", tags=["worker"])


@router.post(
    "/enqueue/process-file",
    summary="สั่งงาน background ประมวลผลไฟล์",
    response_description="Job ID ที่ใช้เช็คสถานะภายหลัง",
)
async def enqueue_process_file(bucket_name: str, object_name: str):
    job = task_queue.enqueue(process_uploaded_file, bucket_name, object_name)
    return {"job_id": job.id, "status": job.get_status()}


@router.get(
    "/status/{job_id}",
    summary="เช็คสถานะของ background job",
)
async def get_job_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception:
        raise HTTPException(status_code=404, detail="ไม่พบ job นี้")
    return {
        "job_id": job.id,
        "status": job.get_status(),
        "result": job.result,
    }