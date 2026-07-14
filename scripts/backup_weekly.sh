#!/usr/bin/env bash
# ===========================================================================
# MIRU Bank Sampah — Backup Mingguan (Full + Off-Server)
# ===========================================================================
# Jadwal: setiap Minggu jam 02:00 WIT via cron
# Output:
#   - Lokal: /opt/miru/backups/weekly/miru_WW_YEAR.dump.gz.gpg
#   - Remote: rsync ke server backup terpisah (jika REMOTE_HOST diisi)
# Retensi: lokal 30 hari, remote 90 hari (diatur di server backup)
# ===========================================================================
set -euo pipefail

# --- Konfigurasi ---
DB_NAME="${DB_NAME:-miru}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-/opt/miru/backups/weekly}"
GPG_PASSPHRASE="${GPG_PASSPHRASE:-}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# Remote backup (opsional — kosongkan jika tidak ada)
REMOTE_HOST="${REMOTE_HOST:-}"
REMOTE_USER="${REMOTE_USER:-}"
REMOTE_PATH="${REMOTE_PATH:-/backup/miru}"

# ISO week number untuk penamaan
YEAR=$(date +%G)
WEEK=$(date +%V)
TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"
OUTPUT_FILE="${BACKUP_DIR}/miru_week${WEEK}_${YEAR}_${TIMESTAMP}.dump.gz.gpg"

# --- Validasi ---
if [ -z "$GPG_PASSPHRASE" ]; then
    echo "ERROR: GPG_PASSPHRASE belum diisi. Backup dibatalkan."
    exit 1
fi

if ! command -v gpg &>/dev/null; then
    echo "ERROR: gpg tidak ditemukan."
    exit 1
fi

mkdir -p "$BACKUP_DIR"

# --- Full backup via pipe: pg_dump → gpg (tanpa file plaintext) ---
echo "[$(date '+%Y-%m-%d %H:%M:%S')] === BACKUP MINGGUAN ==="
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Database: $DB_NAME"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Week: $WEEK / $YEAR"

export PGPASSWORD="${DB_PASSWORD:-}"

pg_dump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --format=custom \
    2>>"${BACKUP_DIR}/backup_weekly.log" | \
gpg --symmetric \
    --cipher-algo AES256 \
    --batch \
    --passphrase "$GPG_PASSPHRASE" \
    --output "$OUTPUT_FILE"

# --- Validasi hasil ---
if [ ! -s "$OUTPUT_FILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: File backup mingguan kosong!"
    rm -f "$OUTPUT_FILE"
    exit 1
fi

BACKUP_SIZE=$(stat --format=%s "$OUTPUT_FILE" 2>/dev/null || echo 0)
BACKUP_SIZE_MB=$((BACKUP_SIZE / 1048576))
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup mingguan: $(basename ${OUTPUT_FILE}) (${BACKUP_SIZE_MB}MB)"

# --- Retensi lokal: hapus backup >30 hari ---
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Retensi lokal: hapus backup > ${RETENTION_DAYS} hari..."
find "$BACKUP_DIR" -name "*.gpg" -type f -mtime "+${RETENTION_DAYS}" -delete
find "$BACKUP_DIR" -name "backup_weekly.log" -type f -mtime "+${RETENTION_DAYS}" -delete

# --- Sync ke server backup terpisah (jika dikonfigurasi) ---
if [ -n "$REMOTE_HOST" ] && [ -n "$REMOTE_USER" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Mengirim backup ke remote: ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}"
    rsync -avz --progress \
        "$BACKUP_DIR/" \
        "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/" \
        2>>"${BACKUP_DIR}/backup_rsync.log"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] rsync selesai."
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] REMOTE_HOST tidak dikonfigurasi. Backup hanya disimpan lokal."
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Untuk keamanan, konfigurasi REMOTE_HOST di .env"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup mingguan SELESAI."
