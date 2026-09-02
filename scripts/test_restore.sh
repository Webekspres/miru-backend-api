#!/usr/bin/env bash
# Isolated restore drill (BACKUP.md §7). Never drops the live DB_NAME.
# Flow: backup live DB → restore into miru_restore_test → /health/ → login → GET deposits.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/_backup_lib.sh
. "${SCRIPT_DIR}/_backup_lib.sh"

miru_load_env

SOURCE_DB="${DB_NAME:-miru}"
TEST_DB="${RESTORE_TEST_DB:-miru_restore_test}"
if [ "$TEST_DB" = "$SOURCE_DB" ]; then
    echo "ERROR: RESTORE_TEST_DB tidak boleh sama dengan DB live (${SOURCE_DB})."
    exit 1
fi

cd "$MIRU_ROOT"

PYTHON="${MIRU_ROOT}/venv/bin/python"
if [ ! -x "$PYTHON" ]; then
    echo "ERROR: ${PYTHON} tidak ditemukan. Pakai venv backend."
    exit 1
fi

if [ -z "${GPG_PASSPHRASE:-}" ]; then
    echo "GPG_PASSPHRASE belum ada di .env — membuat passphrase lokal (tidak dicetak)."
    "$PYTHON" - "$MIRU_ROOT/.env" <<'PY'
import secrets
import sys
from pathlib import Path
env = Path(sys.argv[1])
text = env.read_text() if env.exists() else ""
if "GPG_PASSPHRASE=" not in text:
    env.write_text(text + "\nGPG_PASSPHRASE=" + secrets.token_urlsafe(32) + "\n")
PY
    miru_load_env
fi

if [ -z "${GPG_PASSPHRASE:-}" ]; then
    echo "ERROR: GPG_PASSPHRASE masih kosong."
    exit 1
fi

miru_require_pg
export PGPASSWORD="${DB_PASSWORD:-}"

WORKDIR="${MIRU_ROOT}/backups/restore-test"
mkdir -p "$WORKDIR"
LOG="${WORKDIR}/RESTORE_TEST_LOG.txt"
OPERATOR="${RESTORE_OPERATOR:-${USER:-unknown}}"
STAMP="$(date -Iseconds)"

count_rows() {
    local db="$1"
    DB_NAME="$db" "$PYTHON" -c \
        "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from django.contrib.auth import get_user_model; from api.models import TransaksiSetoran; print(get_user_model().objects.count(), TransaksiSetoran.objects.count())"
}

echo "=== Test restore MIRU ==="
echo "Sumber: ${SOURCE_DB}  Target isolasi: ${TEST_DB}"
echo "Operator: ${OPERATOR}"
echo "Waktu: ${STAMP}"

read -r LIVE_USERS LIVE_DEPOSITS < <(count_rows "$SOURCE_DB")
echo "Live counts: users=${LIVE_USERS} deposits=${LIVE_DEPOSITS}"

echo "[1/6] backup.sh (database ${SOURCE_DB})"
DB_NAME="$SOURCE_DB" BACKUP_DIR="$WORKDIR" bash "${SCRIPT_DIR}/backup.sh"
BACKUP_FILE="$(cat "${WORKDIR}/latest.path")"
if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: backup.sh tidak menghasilkan file."
    exit 1
fi
echo "Backup: $(basename "$BACKUP_FILE")"

echo "[2/6] CREATE DATABASE ${TEST_DB}"
miru_ensure_database "$TEST_DB"

echo "[3/6] restore.sh --yes → ${TEST_DB}"
DB_NAME="$TEST_DB" bash "${SCRIPT_DIR}/restore.sh" --yes "$BACKUP_FILE"

echo "[4/6] bandingkan jumlah record"
read -r REST_USERS REST_DEPOSITS < <(count_rows "$TEST_DB")
echo "Restored counts: users=${REST_USERS} deposits=${REST_DEPOSITS}"
if [ "$REST_USERS" != "$LIVE_USERS" ] || [ "$REST_DEPOSITS" != "$LIVE_DEPOSITS" ]; then
    echo "FAIL: jumlah record tidak sama dengan sumber."
    echo "users ${LIVE_USERS}→${REST_USERS}  deposits ${LIVE_DEPOSITS}→${REST_DEPOSITS}"
    RESULT="gagal"
    {
        echo "tanggal=${STAMP}"
        echo "operator=${OPERATOR}"
        echo "hasil=${RESULT}"
        echo "alasan=count mismatch users ${LIVE_USERS}->${REST_USERS} deposits ${LIVE_DEPOSITS}->${REST_DEPOSITS}"
    } >"$LOG"
    exit 1
fi

PORT="${RESTORE_TEST_PORT:-18000}"
echo "[5/6] runserver 127.0.0.1:${PORT} (DB_NAME=${TEST_DB})"
DB_NAME="$TEST_DB" "$PYTHON" manage.py runserver "127.0.0.1:${PORT}" --noreload \
    >"${WORKDIR}/runserver.log" 2>&1 &
SERVER_PID=$!

cleanup_server() {
    if [ -n "${SERVER_PID:-}" ]; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
}
trap cleanup_server EXIT

ready=0
for _ in $(seq 1 40); do
    if curl -sf "http://127.0.0.1:${PORT}/health/" >/dev/null 2>&1; then
        ready=1
        break
    fi
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "ERROR: runserver mati. Lihat ${WORKDIR}/runserver.log"
        exit 1
    fi
    sleep 0.5
done
if [ "$ready" -ne 1 ]; then
    echo "ERROR: /health/ tidak merespons di port ${PORT}"
    exit 1
fi

echo "[6/6] /health/ + login admin + GET /api/deposits/"
set +e
RESTORE_BASE_URL="http://127.0.0.1:${PORT}" \
    EXPECT_DEPOSIT_COUNT="$LIVE_DEPOSITS" \
    "$PYTHON" "${SCRIPT_DIR}/verify_restored_api.py"
VERIFY_RC=$?
set -e

cleanup_server
trap - EXIT
SERVER_PID=""

if [ "$VERIFY_RC" -eq 0 ]; then
    echo "[cleanup] DROP DATABASE ${TEST_DB}"
    miru_drop_database "$TEST_DB"
    RESULT="lolos"
else
    echo "FAIL verifikasi HTTP (exit ${VERIFY_RC}). Database ${TEST_DB} dibiarkan untuk debug."
    RESULT="gagal"
fi

{
    echo "tanggal=${STAMP}"
    echo "operator=${OPERATOR}"
    echo "hasil=${RESULT}"
    echo "sumber_db=${SOURCE_DB}"
    echo "target_db=${TEST_DB}"
    echo "backup_file=$(basename "$BACKUP_FILE")"
    echo "users=${LIVE_USERS}"
    echo "deposits=${LIVE_DEPOSITS}"
    echo "health=/health/ database=connected"
    echo "login=admin"
    echo "read=/api/deposits/"
} >"$LOG"

echo "Hasil: ${RESULT}  log: ${LOG}"
exit "$VERIFY_RC"
