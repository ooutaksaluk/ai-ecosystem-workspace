from fastapi import APIRouter, Depends
from app.domains.labeling.service import get_client

router = APIRouter(prefix="/labeling", tags=["labeling"])

@router.get("/projects")
def list_projects(client=Depends(get_client)):
    """ดึงรายการ project ทั้งหมดจาก Label Studio"""
    projects = client.projects.list()
    return projects