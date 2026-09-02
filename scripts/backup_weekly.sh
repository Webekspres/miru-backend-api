#!/usr/bin/env bash
# Weekly encrypted pg_dump + optional rsync. Cron: Sunday 02:00 WIT.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/_backup_lib.sh
. "${SCRIPT_DIR}/_backup_lib.sh"

miru_load_env

DB_NAME="${DB_NAME:-miru}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-${MIRU_ROOT}/backups/weekly}"
GPG_PASSPHRASE="${GPG_PASSPHRASE:-}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
REMOTE_HOST="${REMOTE_HOST:-}"
REMOTE_USER="${REMOTE_USER:-}"
REMOTE_PATH="${REMOTE_PATH:-/backup/miru}"

YEAR="$(date +%G)"
WEEK="$(date +%V)"
TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"
OUTPUT_FILE="${BACKUP_DIR}/miru_week${WEEK}_${YEAR}_${TIMESTAMP}.dump.gz.gpg"

if [ -z "$GPG_PASSPHRASE" ]; then
    echo "ERROR: GPG_PASSPHRASE belum diisi. Backup dibatalkan."
    exit 1
fi

if ! command -v gpg >/dev/null 2>&1; then
    echo "ERROR: gpg tidak ditemukan."
    exit 1
fi

miru_require_pg
mkdir -p "$BACKUP_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === BACKUP MINGGUAN ==="
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Database: $DB_NAME"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Week: $WEEK / $YEAR"

export PGPASSWORD="${DB_PASSWORD:-}"

miru_pg_dump 2>>"${BACKUP_DIR}/backup_weekly.log" | miru_gpg_encrypt "$OUTPUT_FILE"

if [ ! -s "$OUTPUT_FILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: File backup mingguan kosong!"
    rm -f "$OUTPUT_FILE"
    exit 1
fi

BACKUP_SIZE="$(stat --format=%s "$OUTPUT_FILE" 2>/dev/null || echo 0)"
BACKUP_SIZE_MB=$((BACKUP_SIZE / 1048576))
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup mingguan: $(basename "${OUTPUT_FILE}") (${BACKUP_SIZE_MB}MB)"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Retensi lokal: hapus backup > ${RETENTION_DAYS} hari..."
find "$BACKUP_DIR" -name "*.gpg" -type f -mtime "+${RETENTION_DAYS}" -delete
find "$BACKUP_DIR" -name "backup_weekly.log" -type f -mtime "+${RETENTION_DAYS}" -delete

if [ -n "$REMOTE_HOST" ] && [ -n "$REMOTE_USER" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Mengirim backup ke remote: ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}"
    rsync -avz --progress \
        "$BACKUP_DIR/" \
        "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/" \
        2>>"${BACKUP_DIR}/backup_rsync.log"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] rsync selesai."
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] REMOTE_HOST tidak dikonfigurasi. Backup hanya disimpan lokal."
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup mingguan SELESAI."
