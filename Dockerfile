FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Binari uv, versi di-pin agar build deterministik
COPY --from=ghcr.io/astral-sh/uv:0.12.8 /uv /uvx /bin/

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.lock /app/
# --system: instal ke site-packages image (setara pip), yang lalu dipakai Gunicorn langsung.
# --no-cache: cegah limbah cache uv menambah ukuran image.
RUN uv pip install --system --no-cache -r requirements.lock

COPY . /app/

EXPOSE 8000

# Gunakan Gunicorn untuk production (override via CMD jika perlu runserver untuk dev)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]