FROM python:3.12-slim

# Zakázání bufferování výstupu a generování pyc souborů
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instalace systémových knihoven pro kompilaci v případě potřeby
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalace Python závislostí
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Zkopírování kódu aplikace a migrací
COPY . .

EXPOSE 8000

# Spuštění migrací a následné nastartování Uvicorn serveru
CMD ["sh", "-c", "alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
