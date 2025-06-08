FROM python:3.11-slim

# نصب وابستگی‌های لازم و locale فارسی
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    gcc \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# تنظیم locale فارسی
RUN sed -i '/fa_IR.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen fa_IR.UTF-8

ENV LANG=fa_IR.UTF-8 \
    LANGUAGE=fa_IR:fa \
    LC_ALL=fa_IR.UTF-8

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
