
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static and apply migrations
CMD ["sh", "-c", "python manage.py migrate && python manage.py setup_binance && gunicorn app.wsgi:application --bind 0.0.0.0:8000"]
