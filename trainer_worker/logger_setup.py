import logging
import os
from datetime import datetime


def setup_logger(job_id: str, log_dir: str = "./logs") -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{log_dir}/train_{job_id}_{timestamp}.log"

    logger = logging.getLogger(job_id)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()   # กันเพิ่ม handler ซ้ำถ้าเรียกฟังก์ชันนี้หลายรอบ

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # เขียนลงไฟล์
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # แสดงบน console ด้วย (เห็นตอนรัน docker compose logs -f)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger, log_filename