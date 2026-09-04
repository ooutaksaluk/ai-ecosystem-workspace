# fastapi_app/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements ก่อน เพื่อให้ Docker cache layer นี้ไว้
# (ถ้าโค้ด app เปลี่ยนแต่ requirements ไม่เปลี่ยน จะไม่ต้อง pip install ใหม่)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy โค้ดจริงเข้าไปทีหลัง
COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]