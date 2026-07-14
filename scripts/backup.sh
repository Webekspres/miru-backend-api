#!/usr/bin/env bash
# ===========================================================================
# MIRU Bank Sampah — Backup Harian Database
# ===========================================================================
# Jadwal: setiap hari jam 03:00 WIT (UTC+9) via cron
# Output:  /opt/miru/backups/daily/miru_YYYY-MM-DD.dump.gz.gpg
# Retensi: 30 hari (file >30 hari otomatis dihapus)
# Enkripsi: GPG symmetric key (gpg --symmetric) via pipe — tanpa file plaintext
# ===========================================================================
set -euo pipefail

# --- Konfigurasi (bisa di-override via env) ---
DB_NAME="${DB_NAME:-miru}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-/opt/miru/backups/daily}"
GPG_PASSPHRASE="${GPG_PASSPHRASE:-}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"
OUTPUT_FILE="${BACKUP_DIR}/miru_${TIMESTAMP}.dump.gz.gpg"

# --- Validasi ---
if [ -z "$GPG_PASSPHRASE" ]; then
    echo "ERROR: GPG_PASSPHRASE belum diisi. Backup dibatalkan."
    exit 1
fi

if ! command -v pg_dump &>/dev/null; then
    echo "ERROR: pg_dump tidak ditemukan. Pastikan PostgreSQL client terinstall."
    exit 1
fi

if ! command -v gpg &>/dev/null; then
    echo "ERROR: gpg tidak ditemukan."
    exit 1
fi

# --- Buat direktori backup ---
mkdir -p "$BACKUP_DIR"

# --- Backup via pipe: pg_dump → gzip → gpg (tanpa file plaintext) ---
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Memulai backup database $DB_NAME..."

export PGPASSWORD="${DB_PASSWORD:-}"

pg_dump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --format=custom \
    2>>"${BACKUP_DIR}/backup.log" | \
gpg --symmetric \
    --cipher-algo AES256 \
    --batch \
    --passphrase "$GPG_PASSPHRASE" \
    --output "$OUTPUT_FILE"

# --- Validasi hasil ---
if [ ! -s "$OUTPUT_FILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: File backup kosong atau gagal dibuat!"
    rm -f "$OUTPUT_FILE"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup selesai: $(basename ${OUTPUT_FILE})"

# --- Hapus backup > RETENTION_DAYS hari ---
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Membersihkan backup lebih dari ${RETENTION_DAYS} hari..."
find "$BACKUP_DIR" -name "*.gpg" -type f -mtime "+${RETENTION_DAYS}" -delete
find "$BACKUP_DIR" -name "backup.log" -type f -mtime "+${RETENTION_DAYS}" -delete

# --- Hitung ukuran backup ---
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Ukuran total folder backup: $TOTAL_SIZE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup harian SELESAI."
