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

## Staging / Production (Docker + PostgreSQL)

Docker Compose is used to spin up the Django app alongside a PostgreSQL database for staging or production.

### 1. Environment Variables
Copy `.env.example` to `.env` and configure:

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

### OTP WhatsApp di local (tanpa provider)

Tanpa kredensial `WA_*`, OTP tidak sampai ke WhatsApp. Untuk uji mobile, set di `.env`:

```env
DEBUG=True
OTP_DEV_FIXED_CODE=123456
```

Lalu masukkan `123456` di layar verifikasi. Detail: [`docs/OTP_DEV.md`](docs/OTP_DEV.md).

### 2. Build and Run
```bash
docker-compose up --build -d
```

### 3. Run Migrations in Docker
```bash
docker-compose exec web python manage.py migrate
```

### 4. Seed Demo Data

Management command `seed_data` mengisi database dengan data demo MIRU.

#### Mode minimal (Fase 1.5 — development awal)

Membuat data inti saja:
- 8 kategori sampah: PET, Gelas Plastik, Kardus, Kertas, Aluminium, Besi, Kaca, Jelantah
- 4 reward: Pulsa, Bibit, Sembako, Alat Kebersihan
- 1 user admin: `admin` / `admin123`

```bash
# Docker
docker compose exec web python manage.py seed_data --minimal --flush

# Local venv (SQLite)
python manage.py seed_data --minimal --flush
```

#### Mode full (200+ records untuk uji integrasi)

Selain data inti di atas, juga membuat koordinator, petugas, 180 nasabah, transaksi setoran, penjemputan, penarikan, pengaduan, mitra, dan penukaran poin.

```bash
# Docker — reset & seed ulang
docker compose exec web python manage.py seed_data --flush

# Custom jumlah nasabah
docker compose exec web python manage.py seed_data --flush --nasabah 200

# Local venv
python manage.py seed_data --flush
```

| Flag | Deskripsi |
|------|-----------|
| `--minimal` | Hanya kategori, reward, dan admin (aman di DB kosong atau setelah `migrate`) |
| `--flush` | Hapus data lama sebelum seed. Mode full: reset semua. Mode minimal: reset admin saja |
| `--nasabah N` | Jumlah nasabah di mode full (default: 180) |

**Akun demo (mode full):**

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | admin |
| `koordinator` | `koordinator123` | koordinator |
| `petugas1` | `petugas123` | petugas |
| `nasabah001` | `nasabah123` | nasabah |

### 5. Run Tests
```bash
docker-compose exec web python manage.py test api.tests --verbosity=2
```

### 6. Mobile — HP Fisik (Windows + Docker Desktop)

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
