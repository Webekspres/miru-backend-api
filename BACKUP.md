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
# 1. Install PostgreSQL client (pg_dump, pg_restore, psql)
#    Opsional di mesin yang sudah menjalankan Postgres via Docker/Podman:
#    scripts memakai `docker/podman exec` ke container yang publish DB_PORT.
sudo apt-get install postgresql-client

# 2. Install GPG
sudo apt-get install gpg

# 3. Install rsync (untuk backup remote)
sudo apt-get install rsync

# 4. Generate GPG key (atau gunakan passphrase symmetric)
gpg --gen-key  # atau gunakan --symmetric dengan passphrase
```

### Environment Variables

Tambahkan ke `.env` (production: `/opt/miru/.env`). Script backup/restore memuat file ini dari root repo.

```bash
# Backup
GPG_PASSPHRASE=<generate-strong-random-passphrase>
BACKUP_DIR=/opt/miru/backups/daily
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

File backup berformat custom `pg_dump` yang **sudah dienkripsi GPG**. Jangan pipe file `.gpg` langsung ke `pg_restore`.

```bash
# 1. Hentikan proses web (gunicorn / runserver / compose web)
#    docker compose stop web

# 2. Recreate database kosong (ini menimpa data live — hanya darurat)
#    docker compose exec db psql -U postgres -c "DROP DATABASE IF EXISTS miru;"
#    docker compose exec db psql -U postgres -c "CREATE DATABASE miru OWNER postgres;"

# 3. Decrypt lalu restore (butuh GPG_PASSPHRASE dari .env)
cd /opt/miru   # atau root repo backend
export DB_NAME=miru
bash scripts/restore.sh /opt/miru/backups/daily/miru_YYYY-MM-DD_HHMMSS.dump.gz.gpg
# ketik RESTORE

# 4. Start ulang web, lalu cek /health/ (data.database harus connected)
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

# 5. Restore (decrypt GPG dulu — jangan pipe file .gpg mentah ke pg_restore)
export DB_NAME=miru
bash scripts/restore.sh /opt/miru/miru_2026-07-14.dump.gz.gpg

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

Backup dan restore **wajib di-test minimal 1×** sebelum go-live.

Jangan drop database live (`DB_NAME`, biasanya `miru`). Uji memakai database isolasi `miru_restore_test`.

**Prosedur:**

```bash
cd backend   # root repo API
# .env harus punya USE_POSTGRES=True, kredensial DB, dan GPG_PASSPHRASE
# (test_restore.sh membuat GPG_PASSPHRASE lokal jika belum ada)

bash scripts/test_restore.sh
```

Script itu menjalankan:

1. `scripts/backup.sh` terhadap database live (hanya baca/dump)
2. `CREATE DATABASE miru_restore_test`
3. `scripts/restore.sh --yes` ke database isolasi
4. Bandingkan jumlah `User` dan `TransaksiSetoran` dengan sumber
5. `runserver` sementara di `127.0.0.1:18000` dengan `DB_NAME=miru_restore_test`
6. `GET /health/` — HTTP 200 dan `data.database=connected`
7. `POST /api/auth/login/` sebagai admin
8. `GET /api/deposits/` (satu halaman baca transaksi)
9. Drop hanya `miru_restore_test` jika semua lolos

Log: `backups/restore-test/RESTORE_TEST_LOG.txt` (folder `backups/` tidak di-commit).

**Kriteria lulus:**
- Restore ke DB isolasi tanpa menyentuh DB live
- Jumlah user dan setoran sama dengan sumber
- `/health/` 200 dan `database=connected`
- Login admin berhasil dan `GET /api/deposits/` mengembalikan data (jika sumber punya setoran)

### Catatan uji

| Tanggal | Operator | Lingkungan | Hasil | Catatan |
|---------|----------|------------|-------|---------|
| 2026-09-02 | habibiahmada | lokal Postgres `miru` → isolasi `miru_restore_test` (live tidak di-drop) | **lolos** | `scripts/test_restore.sh`: dump GPG, restore, `/health/` 200 `database=connected`, login admin, `GET /api/deposits/` count=1 |

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
| `pg_dump: error: connection to server` | DB_HOST salah atau DB tidak running | Cek `docker compose ps` / `podman ps`, pastikan db running |
| `.env` error `$'\r'` | File `.env` pakai CRLF (Windows) | Script sudah strip CR saat load; atau konversi ke LF |
| Restore mengenai DB live padahal `DB_NAME` di-export | `.env` menimpa environment | Script **tidak** menimpa variabel yang sudah di-set (penting untuk `miru_restore_test`) |
| `gpg: decryption failed` | GPG_PASSPHRASE salah | Cek `.env`, pastikan passphrase sesuai |
| `pg_restore: error: could not execute` | Database masih terpakai | Hentikan service web, atau restore ke DB isolasi |
| `rsync: connection refused` | Remote server tidak reachable | Cek koneksi: `ssh backup_user@backup_host` |
| Backup file terlalu besar (>1GB) | Banyak data | Pertimbangkan `--compress=9` atau partisi |
| `Permission denied` saat cron | User cron tidak punya akses | Jalankan cron sebagai root atau user deploy |

---

## Referensi

- `scripts/backup.sh` — backup harian (`pg_dump` custom + GPG)
- `scripts/backup_weekly.sh` — backup mingguan + rsync remote
- `scripts/restore.sh` — restore interaktif (`--yes` hanya untuk uji isolasi)
- `scripts/test_restore.sh` — drill restore sebelum go-live (BACKUP.md §7)
- `scripts/verify_restored_api.py` — cek HTTP `/health/`, login, `GET /api/deposits/`
- `06-system-constraints.md` §7 — Backup & Maintenance
- `05-business-rules-sops.md` §N — Aturan Arsip & Retensi Data
- `09-data-dictionary.md` §I.4 — Domain & Server info
