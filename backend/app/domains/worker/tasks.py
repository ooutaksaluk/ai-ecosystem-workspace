import time
from app.domains.storage import service as storage_service


def process_uploaded_file(bucket_name: str, object_name: str) -> dict:
    """
    ตัวอย่างงาน background: จำลองการประมวลผลไฟล์หลังอัปโหลด
    เช่น resize รูป, extract metadata, หรือส่งเข้า Label Studio
    """
    time.sleep(5)  # จำลองงานหนัก
    files = storage_service.list_objects(bucket_name)
    return {
        "status": "done",
        "bucket": bucket_name,
        "object": object_name,
        "total_files_in_bucket": len(files),
    }


def sync_label_studio_project(project_id: int) -> dict:
    """ตัวอย่างงาน: sync ข้อมูลกับ Label Studio แบบ async"""
    # เรียก label-studio-sdk ตรงนี้
    return {"status": "synced", "project_id": project_id}