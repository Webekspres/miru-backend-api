#!/usr/bin/env bash
# Restore encrypted custom-format dump into DB_NAME.
# Usage: restore.sh [--yes] /path/to/miru_....dump.gz.gpg
# --yes skips the RESTORE confirmation (for scripts/test_restore.sh only).
# This overwrites objects in DB_NAME. Never point DB_NAME at live data unless
# you intend a production restore.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/_backup_lib.sh
. "${SCRIPT_DIR}/_backup_lib.sh"

miru_load_env

YES=0
ENCRYPTED_FILE=""
while [ $# -gt 0 ]; do
    case "$1" in
        --yes|-y)
            YES=1
            shift
            ;;
        -*)
            echo "ERROR: opsi tidak dikenal: $1"
            echo "Contoh: $0 [--yes] /opt/miru/backups/daily/miru_2026-07-14.dump.gz.gpg"
            exit 1
            ;;
        *)
            ENCRYPTED_FILE="$1"
            shift
            ;;
    esac
done

if [ -z "$ENCRYPTED_FILE" ]; then
    echo "ERROR: Tentukan file backup yang akan di-restore."
    echo "Contoh: $0 /opt/miru/backups/daily/miru_2026-07-14.dump.gz.gpg"
    exit 1
fi

if [ ! -f "$ENCRYPTED_FILE" ]; then
    echo "ERROR: File tidak ditemukan: ${ENCRYPTED_FILE}"
    exit 1
fi

DB_NAME="${DB_NAME:-miru}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
GPG_PASSPHRASE="${GPG_PASSPHRASE:-}"

if [ -z "$GPG_PASSPHRASE" ]; then
    echo "ERROR: GPG_PASSPHRASE belum diisi. Set di .env atau export manual."
    exit 1
fi

if ! command -v gpg >/dev/null 2>&1; then
    echo "ERROR: gpg tidak ditemukan."
    exit 1
fi

miru_require_pg

echo "PERINGATAN: restore menimpa objek di database ${DB_NAME}"
echo "File backup:  ${ENCRYPTED_FILE}"
echo "Database:     ${DB_NAME}@${DB_HOST}:${DB_PORT}"
echo "User:         ${DB_USER}"

if [ "$YES" -ne 1 ]; then
    printf "Lanjutkan restore? (ketik 'RESTORE' untuk konfirmasi): "
    read -r CONFIRM
    if [ "$CONFIRM" != "RESTORE" ]; then
        echo "Restore dibatalkan."
        exit 1
    fi
fi

export PGPASSWORD="${DB_PASSWORD:-}"

echo "[1/2] Mendekripsi & merestore backup..."
RESTORE_ARGS=()
if [ "${RESTORE_VERBOSE:-0}" = 1 ]; then
    RESTORE_ARGS+=(--verbose)
fi

set +e
set +u
set +o pipefail
miru_gpg_decrypt "$ENCRYPTED_FILE" | miru_pg_restore "${RESTORE_ARGS[@]}"
_pipe=("${PIPESTATUS[@]}")
set -e
set -u
set -o pipefail
gpg_rc=1
restore_rc=0
if [ "${#_pipe[@]}" -ge 1 ]; then
    gpg_rc="${_pipe[0]}"
fi
if [ "${#_pipe[@]}" -ge 2 ]; then
    restore_rc="${_pipe[1]}"
fi

if [ "$gpg_rc" -ne 0 ]; then
    echo "ERROR: dekripsi GPG gagal (exit ${gpg_rc})."
    exit 1
fi

if [ "$restore_rc" -ne 0 ]; then
    echo "CATATAN: pg_restore exit ${restore_rc} (sering warning DROP/ACL). Verifikasi jumlah record."
fi

echo "[2/2] Restore selesai (tanpa file plaintext)."
echo "Database ${DB_NAME} dikembalikan dari $(basename "${ENCRYPTED_FILE}")."
echo "Verifikasi: curl -f http://127.0.0.1:8000/health/  (harus data.database=connected)"
