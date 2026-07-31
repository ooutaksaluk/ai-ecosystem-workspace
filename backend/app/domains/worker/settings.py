"""
ARQ Worker Settings
รัน worker: uv run arq worker_settings.WorkerSettings
"""

from arq.connections import RedisSettings

from backend.app.core.config import settings


async def startup(ctx):
    print(f"Worker starting up... connected to {settings.REDIS_URL}")


async def shutdown(ctx):
    print("Worker shutting down...")


async def simple_work(ctx, *args, **kwargs) -> dict:
    """
    Function ทดสอบ — แสดง job data ทั้งหมดที่ ARQ ส่งมาให้ผ่าน ctx
    """
    job_data = {
        "job_id": ctx.get("job_id"),
        "job_try": ctx.get("job_try"),
        "enqueue_time": ctx.get("enqueue_time"),
        "score": ctx.get("score"),
        "args": args,
        "kwargs": kwargs,
    }

    print("=" * 50)
    print("JOB DATA")
    print("=" * 50)
    for key, value in job_data.items():
        print(f"{key:15}: {value}")
    print("=" * 50)

    return job_data


class WorkerSettings:
    functions = [simple_work]
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        database=settings.REDIS_DB,
    )
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 20
    keep_result = 3600
