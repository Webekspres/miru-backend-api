FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Binari uv, versi di-pin agar build deterministik
COPY --from=ghcr.io/astral-sh/uv:0.12.8 /uv /uvx /bin/

WORKDIR /app

# Toolchain kompilasi hanya dibutuhkan di stage build ini — tidak ikut
# ke image runtime akhir (lihat stage kedua di bawah).
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.lock /app/
RUN uv venv /opt/venv
# --no-cache: cegah limbah cache uv menambah ukuran image.
RUN uv pip install --python /opt/venv/bin/python --no-cache -r requirements.lock


FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# UID/GID 1000 cocok dengan user host default (Linux Debian/Ubuntu) agar
# bind-mount `.:/app` di docker-compose dev tetap bisa ditulis.
RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --no-create-home app

# Hanya venv terinstal (tanpa gcc/libpq-dev) yang disalin dari stage build.
COPY --from=builder /opt/venv /opt/venv
COPY . /app/
RUN chown -R app:app /app

USER app

EXPOSE 8000

# Gunakan Gunicorn untuk production (override via CMD jika perlu runserver untuk dev)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
