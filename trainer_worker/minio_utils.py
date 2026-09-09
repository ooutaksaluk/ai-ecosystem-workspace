import os
import tempfile
from minio import Minio

# กำหนด Client การเชื่อมต่อ MinIO
minio_client = Minio(
    os.getenv("MINIO_ENDPOINT", "minio:9000"),
    access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
    secure=False,
)

def ensure_buckets_exist(buckets: list[str]):
    """ตรวจสอบและสร้าง Buckets หากยังไม่มีในระบบ"""
    for bucket in buckets:
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)

def download_from_minio(bucket_name: str, object_prefix: str) -> str:
    """
    ดาวน์โหลด Folder/Files ทั้งหมดภายใต้ Prefix ที่กำหนดจาก MinIO มาไว้ใน Temp Directory
    """
    local_dir = tempfile.mkdtemp()
    local_path = os.path.join(local_dir, os.path.basename(object_prefix.rstrip("/")))
    
    objects = minio_client.list_objects(bucket_name, prefix=object_prefix, recursive=True)

    for obj in objects:
        # คำนวณ Relative Path เพื่อสร้างโครงสร้าง Directory ฝั่ง Local ให้ตรงกัน
        relative_path = os.path.relpath(obj.object_name, object_prefix)
        target_path = os.path.join(local_path, relative_path)
        
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        minio_client.fget_object(bucket_name, obj.object_name, target_path)

    return local_path

def upload_to_minio(bucket_name: str, local_path: str, destination_prefix: str) -> str:
    """
    อัปโหลดไฟล์หรือโฟลเดอร์จาก Local ขึ้น MinIO ตาม Destination Prefix ที่กำหนด
    """
    destination_prefix = destination_prefix.strip("/")
    
    if os.path.isfile(local_path):
        # กรณีเป็นไฟล์เดี่ยว
        object_name = f"{destination_prefix}/{os.path.basename(local_path)}"
        minio_client.fput_object(bucket_name, object_name, local_path)
    elif os.path.isdir(local_path):
        # กรณีเป็นโฟลเดอร์ (สแกนอัปโหลดไฟล์ย่อยทั้งหมด)
        for root, _, files in os.walk(local_path):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, local_path)
                object_name = f"{destination_prefix}/{relative_path}".replace("\\", "/")
                
                minio_client.fput_object(bucket_name, object_name, full_path)

    return f"{bucket_name}/{destination_prefix}"