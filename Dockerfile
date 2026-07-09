FROM python:3.11-slim

WORKDIR /app

# نصب پیش‌نیازهای سیستمی
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# کپی فایل‌ها
COPY requirements.txt .
COPY bot.py .

# نصب کتابخانه‌ها با pip
RUN pip install --no-cache-dir -r requirements.txt

# اجرای ربات
CMD ["python", "bot.py"]