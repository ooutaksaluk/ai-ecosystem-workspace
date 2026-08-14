from fastapi import APIRouter, UploadFile, File, HTTPException
from app.domains.storage import service
import shutil, tempfile, os

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post(
    "/upload/{bucket_name}",
    summary="อัปโหลดไฟล์เข้า MinIO",
    response_description="Path ของ object ที่อัปโหลดสำเร็จ",
)
async def upload(bucket_name: str, file: UploadFile = File(...)):
    """
    อัปโหลดไฟล์เข้า bucket ที่ระบุ
    - **bucket_name**: ชื่อ bucket ปลายทาง
    - **file**: ไฟล์ที่ต้องการอัปโหลด
    """
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        object_path = service.upload_file(bucket_name, file.filename, tmp_path)
        return {"object_path": object_path}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(tmp_path)


@router.get(
    "/download-url/{bucket_name}/{object_name}",
    summary="ขอ presigned URL สำหรับดาวน์โหลด",
)
async def download_url(bucket_name: str, object_name: str):
    return {"url": service.get_download_url(bucket_name, object_name)}


@router.get(
    "/list/{bucket_name}",
    summary="แสดงรายการไฟล์ทั้งหมดใน bucket",
)
async def list_files(bucket_name: str):
    return {"objects": service.list_objects(bucket_name)}