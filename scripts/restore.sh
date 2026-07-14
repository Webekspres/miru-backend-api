#!/usr/bin/env bash
# ===========================================================================
# MIRU Bank Sampah — Restore Database dari Encrypted Backup
# ===========================================================================
#
# Cara pakai:
#   1. SSH ke server
#   2. Tentukan file backup yang akan di-restore
#   3. Jalankan: ./scripts/restore.sh /path/to/backup.dump.gz.gpg
#
# Prasyarat:
#   - GPG_PASSPHRASE terisi di environment atau .env
#   - PostgreSQL client (pg_restore) terinstall
#   - Database target sudah ada (dibuat via createdb jika perlu)
#
# ⚠️ PERHATIAN:
#   - Script ini akan MENIMPA data yang ada di database
#   - Pastikan sudah backup data terbaru SEBELUM restore
#   - Restore hanya boleh dilakukan oleh ADMIN SISTEM (Harorld Sopacua)
#     atau DEVELOPER (PT Webekspres) atas persetujuan Koordinator Program
# ===========================================================================
set -euo pipefail

# --- Warna untuk output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║     MIRU Bank Sampah — Database Restore Tool           ║${NC}"
echo -e "${YELLOW}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# --- Cek argumen ---
if [ $# -lt 1 ]; then
    echo -e "${RED}ERROR: Tentukan file backup yang akan di-restore.${NC}"
    echo "Contoh: $0 /opt/miru/backups/daily/miru_2026-07-14.dump.gz.gpg"
    exit 1
fi

ENCRYPTED_FILE="$1"

if [ ! -f "$ENCRYPTED_FILE" ]; then
    echo -e "${RED}ERROR: File tidak ditemukan: ${ENCRYPTED_FILE}${NC}"
    exit 1
fi

# --- Konfigurasi ---
DB_NAME="${DB_NAME:-miru}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
GPG_PASSPHRASE="${GPG_PASSPHRASE:-}"

# --- Validasi GPG passphrase ---
if [ -z "$GPG_PASSPHRASE" ]; then
    echo -e "${RED}ERROR: GPG_PASSPHRASE belum diisi. Set di .env atau export manual.${NC}"
    exit 1
fi

# --- Konfirmasi ---
echo -e "${YELLOW}⚠️  PERINGATAN: Ini akan menimpa database ${DB_NAME}${NC}"
echo ""
echo "File backup:  ${ENCRYPTED_FILE}"
echo "Database:     ${DB_NAME}@${DB_HOST}:${DB_PORT}"
echo "User:         ${DB_USER}"
echo ""
read -p "Lanjutkan restore? (ketik 'RESTORE' untuk konfirmasi): " CONFIRM
if [ "$CONFIRM" != "RESTORE" ]; then
    echo -e "${RED}Restore dibatalkan.${NC}"
    exit 1
fi

# --- Decrypt & restore via pipe (tanpa file plaintext) ---
echo ""
echo -e "${GREEN}[1/2] Mendekripsi & merestore backup...${NC}"
export PGPASSWORD="${DB_PASSWORD:-}"

gpg --decrypt \
    --batch \
    --passphrase "$GPG_PASSPHRASE" \
    "$ENCRYPTED_FILE" 2>/dev/null | \
pg_restore \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --clean \
    --if-exists \
    --verbose \
    2>&1 | tail -20

echo -e "${GREEN}      Restore selesai.${NC}"

# --- Tidak ada file temporary yang perlu dibersihkan (pipe langsung) ---
echo -e "${GREEN}[2/2] Selesai (tanpa file temporary).${NC}"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  RESTORE SELESAI                                       ║${NC}"
echo -e "${GREEN}║  Database ${DB_NAME} telah dikembalikan dari backup:   ║${NC}"
echo -e "${GREEN}║  $(basename ${ENCRYPTED_FILE})                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Catatan:${NC}"
echo "- Verifikasi data: curl -f http://localhost:8000/health/"
echo "- Jika ada masalah, hubungi developer di webekspres.id"
echo "- Laporkan restore ke Koordinator Program (Arfan)"
