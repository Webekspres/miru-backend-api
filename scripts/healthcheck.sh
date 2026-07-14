#!/usr/bin/env bash
# ===========================================================================
# MIRU Bank Sampah — Uptime Monitoring Script
# ===========================================================================
# Mengecek endpoint /health/ secara periodik dan mengirim alert jika down.
#
# Cara pakai:
#   ./scripts/healthcheck.sh                    # Cek sekali
#   ./scripts/healthcheck.sh --watch            # Cek setiap 60 detik
#   ./scripts/healthcheck.sh --watch --interval 300  # Cek setiap 5 menit
#
# Jadwal cron (cek tiap 5 menit):
#   */5 * * * * /opt/miru/scripts/healthcheck.sh >> /var/log/miru_health.log 2>&1
# ===========================================================================
set -euo pipefail

# --- Konfigurasi ---
HEALTH_URL="${HEALTH_URL:-http://localhost:8000/health/}"
ALERT_EMAIL="${ALERT_EMAIL:-admin@mirubanksampah.id}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"
LOG_FILE="${LOG_FILE:-/var/log/miru_health.log}"
TIMEOUT_SEC="${TIMEOUT_SEC:-10}"

# --- Warna ---
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# --- Fungsi alert ---
send_alert() {
    local subject="$1"
    local message="$2"
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S WIT')"

    # Email (via sendmail/mailutils — harus diinstall)
    echo "[${timestamp}] ${message}" | mail -s "[MIRU] ${subject}" "${ALERT_EMAIL}" 2>/dev/null || true

    # Slack webhook (opsional)
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -s -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 *${subject}*\\n${message}\\nServer: $(hostname)\\nWaktu: ${timestamp}\"}" \
            "$SLACK_WEBHOOK" 2>/dev/null || true
    fi
}

# --- Cek health ---
check_health() {
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"

    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT_SEC" "$HEALTH_URL" 2>/dev/null || echo "000")

    local response_body
    response_body=$(curl -s --max-time "$TIMEOUT_SEC" "$HEALTH_URL" 2>/dev/null || echo "")

    if [ "$http_code" = "200" ]; then
        # Cek body response — pastikan status=ok
        local db_status
        db_status=$(echo "$response_body" | python -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('database','unknown'))" 2>/dev/null || echo "parse_error")

        if [ "$db_status" = "connected" ]; then
            echo -e "${GREEN}[${timestamp}] OK${NC} — Health check passed (HTTP ${http_code}, DB: ${db_status})"
            return 0
        else
            echo -e "${RED}[${timestamp}] DEGRADED${NC} — API responds ${http_code} but DB status: ${db_status}"
            send_alert "Health Check: Degraded" "API responds HTTP ${http_code} but database status: ${db_status}"
            return 1
        fi
    else
        echo -e "${RED}[${timestamp}] DOWN${NC} — Health check failed (HTTP ${http_code})"
        send_alert "❗ Health Check: DOWN" "Server tidak merespon dengan HTTP 200. Status: HTTP ${http_code}. URL: ${HEALTH_URL}"
        return 1
    fi
}

# --- Mode: sekali jalan ---
if [ "${1:-}" != "--watch" ]; then
    check_health
    exit $?
fi

# --- Mode: watch (loop) ---
INTERVAL="${2:-60}"
if [ "$1" = "--watch" ] && [ "${3:-}" = "--interval" ] && [ -n "${4:-}" ]; then
    INTERVAL="$4"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] MIRU Uptime Monitor — started (interval: ${INTERVAL}s, URL: ${HEALTH_URL})"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Alert: email=${ALERT_EMAIL}, slack=$([ -n \"$SLACK_WEBHOOK\" ] && echo 'yes' || echo 'no')"

while true; do
    check_health
    sleep "$INTERVAL"
done
