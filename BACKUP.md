# Backup & Recovery — MIRU Bank Sampah

> **Dokumen:** Prosedur backup, restore, dan recovery untuk sistem MIRU Bank Sampah.
> **Sumber:** Jawaban Persyaratan §6.5.6, Constraints §7, Security §9, SOP Arsip §N.

---

## Daftar Isi

1. [Strategi Backup](#1-strategi-backup)
2. [Jadwal & Retensi](#2-jadwal--retensi)
3. [Lokasi Penyimpanan](#3-lokasi-penyimpanan)
4. [Prasyarat](#4-prasyarat)
5. [Cara Setup Cron](#5-cara-setup-cron)
6. [Prosedur Restore](#6-prosedur-restore)
7. [Test Restore](#7-test-restore)
8. [Otorisasi & Keamanan](#8-otorisasi--keamanan)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Strategi Backup

| Jenis | Frekuensi | Metode | Enkripsi | Retensi |
|-------|-----------|--------|----------|---------|
| **Harian** | Setiap hari, 03:00 WIT | `pg_dump` (custom) | GPG AES-256 | 30 hari |
| **Mingguan** | Setiap Minggu, 02:00 WIT | `pg_dump` (custom) + rsync remote | GPG AES-256 | 30 hari lokal, 90 hari remote |
| **Bulanan** (manual) | Akhir bulan | `pg_dump` + arsip offline | GPG AES-256 | 5 tahun (arsip) |

### Format File Backup

```
/opt/miru/backups/
├── daily/
│   ├── miru_2026-07-14_030001.dump.gz.gpg      # Backup harian
│   └── backup.log                               # Log harian
├── weekly/
│   ├── miru_week29_2026_2026-07-14_020001.dump.gz.gpg  # Backup mingguan
│   └── backup_weekly.log                               # Log mingguan
└── monthly/ (manual)
    └── miru_2026-07_arsip.dump.gz.gpg
```

---

## 2. Jadwal & Retensi

### Backup Harian
- **Waktu:** 03:00 WIT (UTC+9) — di luar jam operasional
- **Perintah:** `scripts/backup.sh`
- **Retensi:** 30 hari — file lebih tua otomatis dihapus
- **Ukuran estimasi:** ~50-200 MB (tergantung jumlah transaksi)

### Backup Mingguan
- **Waktu:** Minggu, 02:00 WIT
- **Perintah:** `scripts/backup_weekly.sh`
- **Retensi lokal:** 30 hari
- **Retensi remote:** 90 hari (diatur di server backup)
- **Sync:** rsync ke server backup terpisah

### Backup Bulanan (Arsip 5 Tahun)
- Dilakukan MANUAL oleh admin sistem setiap akhir bulan
- Disimpan di media eksternal (HDD eksternal / cloud storage)
- Retensi: **minimal 5 tahun** (SOP Arsip §N)

---

## 3. Lokasi Penyimpanan

### Lokasi Utama (Server Produksi)
```
/opt/miru/backups/
```
- Backup disimpan di volume terpisah dari database
- **JANGAN** simpan backup di direktori yang sama dengan database PostgreSQL

### Lokasi Remote (Backup Terpisah)
- Server backup terpisah dikonfigurasi via env variable:
  ```
  REMOTE_HOST=backup.mirubanksampah.id
  REMOTE_USER=backup
  REMOTE_PATH=/backup/miru
  ```
- Akses via SSH key (bukan password)
- Backup remote sebagai **cadangan jika server utama down**

---

## 4. Prasyarat

### Di Server Produksi

```bash
# 1. Install PostgreSQL client (pg_dump, pg_restore)
sudo apt-get install postgresql-client

# 2. Install GPG
sudo apt-get install gpg

# 3. Install rsync (untuk backup remote)
sudo apt-get install rsync

# 4. Generate GPG key (atau gunakan passphrase symmetric)
gpg --gen-key  # atau gunakan --symmetric dengan passphrase
```

### Environment Variables

Tambahkan ke `/opt/miru/.env`:

```bash
# Backup
GPG_PASSPHRASE=<generate-strong-random-passphrase>
BACKUP_DIR=/opt/miru/backups
RETENTION_DAYS=30

# Remote backup (opsional)
REMOTE_HOST=backup.mirubanksampah.id
REMOTE_USER=backup
REMOTE_PATH=/backup/miru
```

> ⚠️ **Simpan GPG_PASSPHRASE di tempat aman** (password manager).
> Tanpa passphrase ini, backup **TIDAK DAPAT** di-restore.

---

## 5. Cara Setup Cron

### Buka crontab (sebagai root atau user deployment)

```bash
sudo crontab -e
```

### Tambahkan jadwal backup

```bash
# MIRU Bank Sampah — Backup Schedule (WIT = UTC+9)

# Harian: setiap hari jam 03:00 WIT
# = 03:00 WIT = 18:00 UTC (previous day)
0 18 * * * cd /opt/miru && bash scripts/backup.sh >> /opt/miru/backups/cron.log 2>&1

# Mingguan: setiap Minggu jam 02:00 WIT
# = 02:00 WIT = 17:00 UTC (Saturday)
0 17 * * 6 cd /opt/miru && bash scripts/backup_weekly.sh >> /opt/miru/backups/cron_weekly.log 2>&1
```

### Verifikasi cron berjalan

```bash
# Cek log backup
tail -f /opt/miru/backups/cron.log
tail -f /opt/miru/backups/cron_weekly.log

# Cek file backup terbaru
ls -la /opt/miru/backups/daily/ | tail -5
ls -la /opt/miru/backups/weekly/ | tail -5
```

---

## 6. Prosedur Restore

### 6.1 Restore Terjadwal (dari file backup)

```bash
# 1. SSH ke server produksi
ssh admin@miru-server

# 2. Cari file backup yang akan di-restore
ls -la /opt/miru/backups/daily/
# Pilih file: miru_2026-07-14_030001.dump.gz.gpg

# 3. Jalankan script restore
cd /opt/miru
bash scripts/restore.sh /opt/miru/backups/daily/miru_2026-07-14_030001.dump.gz.gpg

# 4. Ikuti instruksi di layar — ketik 'RESTORE' untuk konfirmasi
```

### 6.2 Restore Darurat (ketika aplikasi tidak bisa jalan)

```bash
# 1. Hentikan container web
docker compose -f docker-compose.yml -f docker-compose.production.yml stop web

# 2. Drop dan recreate database
docker compose exec db psql -U postgres -c "DROP DATABASE IF EXISTS miru;"
docker compose exec db psql -U postgres -c "CREATE DATABASE miru OWNER postgres;"

# 3. Restore langsung dari container db
docker compose exec -T db pg_restore -U postgres -d miru --clean < /path/to/backup.dump.gz.gpg

# 4. Start container web
docker compose -f docker-compose.yml -f docker-compose.production.yml start web
```

### 6.3 Restore di Server Baru (migrasi)

```bash
# 1. Setup server baru dengan Docker
git clone <repo> /opt/miru
cd /opt/miru
cp .env.example .env
# Isi .env dengan konfigurasi yang sesuai

# 2. Copy file backup ke server baru
scp backup@miru-server:/opt/miru/backups/daily/miru_2026-07-14.dump.gz.gpg /opt/miru/

# 3. Start database
docker compose up -d db

# 4. Tunggu hingga db siap
docker compose exec db pg_isready -U postgres

# 5. Restore
docker compose exec -T db pg_restore -U postgres -d miru --clean < /path/to/backup.dump.gz.gpg

# 6. Jalankan migrasi (jika ada schema change)
docker compose run --rm web python manage.py migrate

# 7. Start semua service
docker compose -f docker-compose.yml -f docker-compose.production.yml up -d
```

### 6.4 Verifikasi Setelah Restore

```bash
# 1. Cek health endpoint
curl http://localhost:8000/health/

# 2. Cek jumlah user
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/users/

# 3. Cek dashboard
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/dashboard/overview/

# 4. Cek log aplikasi
docker compose logs --tail=50 web
```

---

## 7. Test Restore

### Sebelum Go-Live

Backup dan restore **WAJIB di-test minimal 1×** sebelum go-live.

**Prosedur Test:**

```bash
# 1. Di server staging (bukan production!)
#    Setup environment staging identik dengan production

# 2. Jalankan backup harian
bash scripts/backup.sh

# 3. Hapus database staging
docker compose exec db psql -U postgres -c "DROP DATABASE IF EXISTS miru_test;"
docker compose exec db psql -U postgres -c "CREATE DATABASE miru_test OWNER postgres;"

# 4. Restore ke database test
export DB_NAME=miru_test
bash scripts/restore.sh /opt/miru/backups/daily/miru_2026-07-14.dump.gz.gpg

# 5. Jalankan health check
curl -f http://localhost:8000/health/

# 6. Verifikasi data: hitung jumlah user, transaksi, dll.
python manage.py shell -c "from api.models import User; print(f'Users: {User.objects.count()}')"
python manage.py shell -c "from api.models import TransaksiSetoran; print(f'Deposits: {TransaksiSetoran.objects.count()}')"
```

**Kriteria Lulus Test:**
- ✅ Database berhasil di-restore tanpa error
- ✅ Jumlah record sesuai dengan sebelum drop
- ✅ Semua endpoint health check return 200
- ✅ Aplikasi bisa login dan menampilkan data

---

## 8. Otorisasi & Keamanan

### Siapa yang Berwenang

| Tindakan | Yang Berwenang | Keterangan |
|----------|---------------|------------|
| Menjalankan backup harian | **Otomatis** (cron) | Tidak perlu intervensi manual |
| Menjalankan backup mingguan | **Otomatis** (cron) | Tidak perlu intervensi manual |
| Melakukan restore data | **Admin Sistem** (Harorld Sopacua) | Wajib koordinasi dengan Koordinator Program |
| Melakukan restore darurat | **Developer** (PT Webekspres) | Atas persetujuan Koordinator Program |
| Mengakses file backup | **Admin Sistem** | File terenkripsi (GPG) |
| Menyimpan GPG passphrase | **Admin Sistem** + **Koordinator Program** | Disimpan di password manager terpisah |

### Prinsip Keamanan

1. **Backup terenkripsi** — file `.dump.gz.gpg` tidak bisa dibaca tanpa passphrase
2. **Backup terpisah** — backup disimpan di server berbeda dari database utama
3. **Akses terbatas** — hanya admin sistem dan developer yang punya akses ke file backup
4. **Audit trail** — setiap restore dicatat di log dan dilaporkan ke Koordinator Program
5. **GPG passphrase** — jangan simpan di repository! Hanya di `.env` production dan password manager

---

## 9. Troubleshooting

| Masalah | Penyebab | Solusi |
|---------|----------|--------|
| `pg_dump: error: connection to server` | DB_HOST salah atau DB tidak running | Cek `docker compose ps`, pastikan db running |
| `gpg: decryption failed: No secret key` | GPG_PASSPHRASE salah | Cek .env, pastikan passphrase sesuai |
| `pg_restore: error: could not execute` | Database masih terpakai | Hentikan service web: `docker compose stop web` |
| `rsync: connection refused` | Remote server tidak reachable | Cek koneksi: `ssh backup_user@backup_host` |
| Backup file terlalu besar (>1GB) | Banyak data | Pertimbangkan `--compress=9` atau partisi |
| `Permission denied` saat cron | User cron tidak punya akses | Jalankan cron sebagai root atau user deploy |

---

## Referensi

- `scripts/backup.sh` — Script backup harian
- `scripts/backup_weekly.sh` — Script backup mingguan + rsync remote
- `scripts/restore.sh` — Script restore interaktif
- `06-system-constraints.md` §7 — Backup & Maintenance
- `05-business-rules-sops.md` §N — Aturan Arsip & Retensi Data
- `09-data-dictionary.md` §I.4 — Domain & Server info
