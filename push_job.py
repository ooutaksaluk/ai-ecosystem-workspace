import json
import redis
from datetime import datetime, timezone

# 1. เชื่อมต่อกับ Redis Server
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# 2. นิยามข้อมูลงาน (Job Payload)
job_payload = {
    "job_id": "job_101",
    "dataset_name": "sentiment_data",
    "dataset_key": "my_dataset_folder",
    "model_name": "bert-base-uncased",
    "epochs": 3,
    "batch_size": 8,
    "scheduled_time": datetime.now(timezone.utc).isoformat()
}

# 3. แปลง Dictionary เป็นข้อความ JSON และ Push เข้าคิวชื่อ 'train_queue'
r.rpush("train_queue", json.dumps(job_payload))

print("ส่ง Job เข้าสู่ train_queue เรียบร้อยแล้ว!")