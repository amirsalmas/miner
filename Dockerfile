FROM python:3.11-slim

WORKDIR /app

# نصب پیش‌نیازهای سیستمی
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# کپی و نصب کتابخانه‌های پایتون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی بقیه فایل‌های پروژه
COPY . .

# دانلود XMRig در زمان بیلد (چون Railway اجازه اجرای فایل exe رو نمی‌ده)
RUN curl -L -o xmrig.tar.gz https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-linux-static-x64.tar.gz \
    && tar -xzf xmrig.tar.gz \
    && mv xmrig-6.21.0/xmrig /usr/local/bin/xmrig \
    && chmod +x /usr/local/bin/xmrig \
    && rm -rf xmrig.tar.gz xmrig-6.21.0

# تنظیم مسیر XMRig در config.py (چون مسیر پیش‌فرض xmrig.exe هست)
ENV XMRIG_PATH=/usr/local/bin/xmrig

# پورت پیش‌فرض Railway
ENV PORT=5000

EXPOSE 5000

CMD ["python", "app.py"]
