from label_studio_sdk import LabelStudio

from app.core.config import settings


def get_client() -> LabelStudio:
    """สร้างและคืนค่า Label Studio client จาก settings"""
    return LabelStudio(
        base_url=settings.LABEL_STUDIO_URL,
        api_key=settings.LABEL_STUDIO_API_KEY,
    )
