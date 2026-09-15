FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# WeasyPrint (PDF) için gerekli sistem kütüphaneleri
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev \
    libcairo2 libcairo-gobject2 shared-mime-info \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput --settings=fleet_manager.settings || true

EXPOSE 8000

CMD ["gunicorn", "fleet_manager.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
