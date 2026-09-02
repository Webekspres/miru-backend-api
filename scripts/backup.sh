#!/usr/bin/env bash
# Daily encrypted pg_dump (custom format → GPG AES-256). Cron: 03:00 WIT.
# Output: $BACKUP_DIR/miru_YYYY-MM-DD_HHMMSS.dump.gz.gpg
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/_backup_lib.sh
. "${SCRIPT_DIR}/_backup_lib.sh"

miru_load_env

DB_NAME="${DB_NAME:-miru}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-${MIRU_ROOT}/backups/daily}"
GPG_PASSPHRASE="${GPG_PASSPHRASE:-}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"
OUTPUT_FILE="${BACKUP_DIR}/miru_${TIMESTAMP}.dump.gz.gpg"

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

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Memulai backup database ${DB_NAME}..."
export PGPASSWORD="${DB_PASSWORD:-}"

miru_pg_dump 2>>"${BACKUP_DIR}/backup.log" | miru_gpg_encrypt "$OUTPUT_FILE"

if [ ! -s "$OUTPUT_FILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: File backup kosong atau gagal dibuat!"
    rm -f "$OUTPUT_FILE"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup selesai: $(basename "${OUTPUT_FILE}")"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Membersihkan backup lebih dari ${RETENTION_DAYS} hari..."
find "$BACKUP_DIR" -name "*.gpg" -type f -mtime "+${RETENTION_DAYS}" -delete
find "$BACKUP_DIR" -name "backup.log" -type f -mtime "+${RETENTION_DAYS}" -delete

TOTAL_SIZE="$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Ukuran total folder backup: ${TOTAL_SIZE}"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup harian SELESAI."
printf '%s\n' "$OUTPUT_FILE" > "${BACKUP_DIR}/latest.path"
