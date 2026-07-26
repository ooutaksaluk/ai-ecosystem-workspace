import logging
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
import os

# สร้างโฟลเดอร์ logs ถ้ายังไม่มี
os.makedirs("logs", exist_ok=True)


class JsonFormatter(logging.Formatter):
    """แปลง log record ให้เป็น JSON string เพื่อให้อ่าน/parse ต่อได้ง่าย"""
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    """
    สร้างและคืนค่า logger สำหรับใช้ในแต่ละโมดูลของโปรเจกต์
    เรียกใช้: logger = get_logger(__name__)
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # ป้องกันการเพิ่ม handler ซ้ำเวลาเรียก get_logger หลายครั้ง
    if not logger.handlers:
        formatter = JsonFormatter()

        # (1) เขียนลงไฟล์ พร้อม rotation
        file_handler = RotatingFileHandler(
            "logs/app.log",
            maxBytes=5_000_000,   # 5MB ต่อไฟล์
            backupCount=3,        # เก็บไฟล์เก่าไว้ 3 ไฟล์
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        # (2) แสดงบน console/stdout ด้วย (สำคัญมากตอนรันใน Docker)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger