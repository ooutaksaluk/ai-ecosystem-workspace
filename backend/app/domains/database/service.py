from sqlalchemy import text
from app.core.database import engine  # engine ที่สร้างไว้แล้วใน core/database.py


async def check_database_connection() -> dict:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"connected": True}
    except Exception as e:
        return {"connected": False, "error": str(e)}