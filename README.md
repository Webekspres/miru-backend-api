# MIRU Bank Sampah - Backend

Backend API for "MIRU Bank Sampah", built with Django REST Framework. Uses SQLite for local dev, PostgreSQL for staging/prod.

## Local Development (SQLite)

Local development doesn't require Docker. It uses SQLite by default.

### 1. Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Migrations & Server
```bash
python manage.py migrate
python manage.py runserver
```

## Docker Lokal (PostgreSQL + MinIO)

Docker Compose di folder `backend/` — service Django bernama **`web`** (termasuk MinIO untuk gambar avatar/edukasi).

### 1. Environment Variables

Copy `.env.example` ke `.env` dan sesuaikan:

| Variable | Description | Default (dev) |
|----------|-------------|---------------|
| `SECRET_KEY` | Django secret key | Required — generate unique for production |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `USE_POSTGRES` | Use PostgreSQL | `True` for Docker |
| `DB_*` | Database credentials | See `.env.example` |
| `CORS_ALLOW_ALL_ORIGINS` | Allow all CORS origins | `True` for local dev |
| `WA_*` | WhatsApp OTP provider | Kosong = stub (lihat `docs/OTP_DEV.md`) |
| `OTP_DEV_FIXED_CODE` | OTP tetap 6 digit (hanya jika `DEBUG=True`) | Kosong |
| `MINIO_*` | Object storage (avatar, edukasi) | Lihat `.env.example` |

### OTP WhatsApp di local (tanpa provider)

Tanpa kredensial `WA_*`, OTP tidak sampai ke WhatsApp. Untuk uji mobile, set di `.env`:

```env
DEBUG=True
OTP_DEV_FIXED_CODE=123456
```

Lalu masukkan `123456` di layar verifikasi. Detail: [`docs/OTP_DEV.md`](docs/OTP_DEV.md).

### 2. Build and Run

```bash
cd backend
docker compose up --build -d
```

### 3. Run Migrations

```bash
docker compose exec web python manage.py migrate
```

### 4. Run Tests

```bash
docker compose exec web python manage.py test api.tests --verbosity=2
```

### 5. Mobile — HP Fisik (Windows + Docker Desktop)

Docker Desktop di Windows sering hanya mem-publish port ke `127.0.0.1`, sehingga HP di Wi‑Fi tidak bisa akses `http://<IP-PC>:8000`.

**Jalankan LAN proxy** (terminal terpisah, setelah `docker compose up`):

```powershell
python scripts/lan_proxy.py --listen-host 0.0.0.0
```

Lalu tes dari browser HP: `http://<IP-PC-WiFi>:8000/health/`

Pastikan `ALLOWED_HOSTS` di `.env` mencakup IP Wi‑Fi PC. Di mobile (`mirumobileapp/lib/config/constants.dart`):

```dart
static const String apiBaseUrl = 'http://192.168.0.228:8000/api';
```

## VPS Staging / Production

Stack deploy di `/opt/miru-staging` (staging) atau `/opt/miru-prod` (production). Service Django bernama **`api`**. Definisi stack staging ada di repo: [`deploy/staging/`](deploy/staging/) — disinkronkan otomatis oleh CI saat push ke branch `staging`.

| Lingkungan | Direktori | Service Django | Image |
|------------|-----------|----------------|-------|
| Staging | `/opt/miru-staging` | `api` | `ghcr.io/webekspres/miru-backend-api:staging` |
| Production | `/opt/miru-prod` | `api` | `ghcr.io/webekspres/miru-backend-api:latest` |

**Services staging:** `db`, `minio`, `minio-init`, `api`, `admin`, `nginx`

MinIO credentials di `.env` VPS (contoh: [`deploy/staging/.env.minio.example`](deploy/staging/.env.minio.example)). CI menambahkan `MINIO_*` otomatis jika belum ada. `MINIO_ENDPOINT` di-set via `docker-compose.yml` (`http://minio:9000`), bukan di `.env`.

Gambar publik dilayani nginx di `https://api.dev.mirubanksampah.id/objects/` → bucket MinIO.

### Migrasi di VPS

```bash
cd /opt/miru-staging   # atau /opt/miru-prod
docker compose exec -T api python manage.py migrate --noinput
```

### Cek MinIO di VPS

```bash
cd /opt/miru-staging
docker compose ps minio
docker compose exec -T api python manage.py shell -c "from django.conf import settings; print(settings.MINIO_ENABLED, settings.MINIO_ENDPOINT)"
```

### Seed Demo Data

Management command `seed_data` mengisi database dengan data demo MIRU.

#### Mode minimal (data inti saja)

Membuat:
- 8 kategori sampah: PET, Gelas Plastik, Kardus, Kertas, Aluminium, Besi, Kaca, Jelantah
- 4 reward: Pulsa, Bibit, Sembako, Alat Kebersihan
- 1 user admin: `admin` / `admin123`

```bash
# VPS staging / production
cd /opt/miru-staging
docker compose exec -T api python manage.py seed_data --minimal --flush

# Docker lokal (service web)
docker compose exec web python manage.py seed_data --minimal --flush

# Local venv (SQLite)
python manage.py seed_data --minimal --flush
```

#### Mode full (200+ records untuk uji integrasi)

Selain data inti di atas, juga membuat koordinator, petugas, 180 nasabah, transaksi setoran, penjemputan, penarikan, pengaduan, mitra, dan penukaran poin. Proses bisa 2–5 menit.

```bash
# VPS staging / production — reset & seed ulang
cd /opt/miru-staging
docker compose exec -T api python manage.py migrate --noinput
docker compose exec -T api python manage.py seed_data --flush

# Custom jumlah nasabah
docker compose exec -T api python manage.py seed_data --flush --nasabah 200

# Docker lokal
docker compose exec web python manage.py seed_data --flush

# Local venv
python manage.py seed_data --flush
```

| Flag | Deskripsi |
|------|-----------|
| `--minimal` | Hanya kategori, reward, dan admin (aman di DB kosong atau setelah `migrate`) |
| `--flush` | Hapus data lama sebelum seed. Mode full: reset semua user non-superuser + transaksi. **Jangan dipakai jika DB sudah berisi data real** |
| `--nasabah N` | Jumlah nasabah di mode full (default: 180) |

**Akun demo (mode full):**

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | admin |
| `koordinator` | `koordinator123` | koordinator |
| `petugas1` | `petugas123` | petugas |
| `pemerintah` | `pemerintah123` | pemerintah |
| `nasabah001` | `nasabah123` | nasabah (saldo & poin tertinggi) |
| `nasabah002` | `nasabah123` | nasabah (saldo & poin tertinggi) |

## API Access & Documentation

| Resource | URL | Kegunaan |
|----------|-----|----------|
| API Base | `http://localhost:8000/api/` | Endpoint REST |
| **Swagger UI** | `http://localhost:8000/api/docs/` | Referensi teknis standar (OpenAPI) |
| **Panduan Alur** | `http://localhost:8000/api/guide/` | Flow per role + contoh request/response |
| ReDoc | `http://localhost:8000/api/redoc/` | Tampilan alternatif OpenAPI |
| OpenAPI Schema | `http://localhost:8000/api/schema/` | JSON schema untuk Postman/codegen |

**Swagger UI** (`/api/docs/`) adalah dokumentasi standar — auto-generated dari kode, dengan JWT auth dan grouping per modul.

**Panduan Alur** (`/api/guide/`) adalah pelengkap onboarding: menu kiri berurutan login → nasabah → petugas → admin, dengan akun demo per role. Jalankan `seed_data` terlebih dahulu.

Export schema ke file (untuk tim frontend):

```bash
python manage.py spectacular --color --file openapi.json
```

### API Routes (English)

| Route | Description |
|-------|-------------|
| `GET/POST /api/users/` | User management |
| `GET/POST /api/waste-categories/` | Waste categories & prices |
| `GET/POST /api/deposits/` | Deposit transactions |
| `GET/POST /api/pickups/` | Waste pickups |
| `GET/POST /api/withdrawals/` | Balance withdrawals |
| `GET/POST /api/rewards/` | Reward catalog |
| `GET/POST /api/reward-redemptions/` | Point redemptions |
| `GET/POST /api/partners/` | Collector partners |
| `GET/POST /api/partner-sales/` | Partner sales |
| `GET/POST /api/complaints/` | Customer complaints |

### Authentication

The API uses JWT for authentication.
- Obtain Token: `POST /api/auth/login/`
- Refresh Token: `POST /api/auth/refresh/`

Pass the token in the `Authorization` header for protected endpoints:
```
Authorization: Bearer <your_access_token>
```

## Related Projects (Repositori GitHub Terpisah)

| Repositori | Description |
|------------|-------------|
| **miru-web-admin** | Panel admin (petugas, admin, koordinator, distrik) — Next.js |
| **mirumobileapp** | Aplikasi mobile nasabah (Flutter) |

> Ketiga proyek MIRU disimpan di repositori GitHub masing-masing. Clone dan jalankan secara terpisah; integrasi hanya melalui REST API.
