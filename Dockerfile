FROM python:3.11-slim

WORKDIR /app

# نصب پیش‌نیازهای سیستمی (مورد نیاز برای yt-dlp)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# کپی فایل requirements
COPY requirements.txt .

# نصب uv و سپس نصب کتابخانه‌ها با uv (بسیار سریع‌تر از pip)
RUN pip install uv && \
    uv pip install --system --no-cache-dir -r requirements.txt

# کپی کد اصلی
COPY bot.py .

# اجرای ربات
CMD ["python", "bot.py"]
