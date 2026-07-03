# 08 — Task List: Backend Development Roadmap

## Fase 1: Setup & Foundation (✅ Selesai)

### 1.1 Project Setup ✅
- [x] Create Django project (`core/`)
- [x] Create `api` app
- [x] Configure `settings.py` (DB, CORS, JWT, DRF)
- [x] Create Dockerfile & docker-compose.yml
- [x] Create `.env.example`
- [x] Install dependencies: DRF, simplejwt, django-filter, cors-headers, drf-spectacular, psycopg2

### 1.2 Database Models ✅
- [x] Create `User` model (extends AbstractUser) with role, saldo, poin
- [x] Create `KategoriSampah` model
- [x] Create `TransaksiSetoran` + `DetailSetoran` models
- [x] Create `Penjemputan` model with status workflow
- [x] Create `PenarikanSaldo` model
- [x] Create `Reward` + `PenukaranPoin` models
- [x] Create `MitraPengepul` + `PenjualanMitra` models
- [x] Create `Pengaduan` model
- [x] Run initial migrations

### 1.3 Core API Setup ✅
- [x] Serializers for all models
- [x] ViewSets for all models
- [x] URL routing with DefaultRouter
- [x] Custom permissions: `IsAdminOrKoordinator`, `IsPetugasOrAdmin`, `IsOwnerOrAdmin`
- [x] JWT auth endpoints (simplejwt)
- [x] drf-spectacular schema config

## Fase 2: Business Logic & Validations

### 2.1 Transaksi Setoran
- [ ] Validate minimal 1 kg per detail dalam setoran
- [ ] Validate nasabah exists and is_active
- [ ] Implement side effects: update saldo, poin, stok (✅ sudah ada di serializer)
- [ ] Add pagination, filtering, search

### 2.2 Penjemputan Workflow
- [ ] Validate estimasi_berat >= 5 kg
- [ ] Validate jadwal not in the past
- [ ] Implement status workflow transitions
- [ ] Only admin can assign petugas and change status

### 2.3 Penarikan Saldo
- [ ] Validate nominal >= 50000
- [ ] Validate saldo nasabah >= nominal
- [ ] Side effect: kurangi saldo saat status → 'selesai' (✅ sudah ada di views.py)
- [ ] Prevent duplicate processing

### 2.4 Penukaran Poin
- [ ] Validate poin nasabah >= poin_dibutuhkan
- [ ] Validate stok reward > 0
- [ ] Side effect: kurangi poin & stok reward saat status → 'selesai'

### 2.5 Penjualan Mitra
- [ ] Validate stok_terkini_kg >= berat_jual_kg
- [ ] Side effect: kurangi stok (✅ sudah ada di views.py)

## Fase 3: Testing & Documentation

### 3.1 Unit Tests
- [ ] Test registrasi nasabah
- [ ] Test JWT auth (login, refresh, invalid token)
- [ ] Test transaksi setoran (success, min berat validation, insufficient balance)
- [ ] Test penjemputan (create, status transitions, permissions)
- [ ] Test penarikan saldo (min nominal, saldo cukup, approval flow)
- [ ] Test penukaran poin (poin cukup, stok reward)
- [ ] Test permissions (nasabah vs petugas vs admin vs koordinator)

### 3.2 API Documentation
- [ ] Add `help_text` to all serializer fields
- [ ] Add tags to drf-spectacular for grouping endpoints
- [ ] Verify Swagger UI renders correctly

## Fase 4: Dashboard & Laporan API

### 4.1 Dashboard Endpoints
- [ ] `GET /api/dashboard/overview/` — Total nasabah, total sampah, saldo total
- [ ] `GET /api/dashboard/grafik-setoran/` — Data grafik setoran per bulan
- [ ] `GET /api/dashboard/aktivitas-terbaru/` — 10 transaksi terbaru

### 4.2 Laporan Endpoints
- [ ] `GET /api/laporan/harian/?tanggal=` — Rekap harian
- [ ] `GET /api/laporan/bulanan/?bulan=&tahun=` — Rekap bulanan
- [ ] `GET /api/laporan/sampah/?start=&end=` — Laporan tonase per periode

## Fase 5: Post-MVP / Future

### 5.1 Peningkatan
- [ ] Rate limiting pada endpoint auth
- [ ] Email notification untuk admin (laporan harian)
- [ ] Export laporan ke Excel (server-side via openpyxl)
- [ ] Logging & monitoring (Sentry or similar)
- [ ] Cache untuk data dashboard (Redis)
- [ ] API versioning (`/api/v2/`)

### 5.2 Optimasi
- [ ] Database indexing untuk query yang lambat
- [ ] Query optimization (select_related, prefetch_related)
- [ ] Pagination tuning
- [ ] Connection pooling untuk PostgreSQL
