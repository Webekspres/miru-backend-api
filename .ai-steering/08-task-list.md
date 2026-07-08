# 08 — Task List: Backend Development Roadmap

> **Dokumen ini** adalah roadmap pengembangan backend MIRU Bank Sampah dari MVP hingga production-ready.
> Urutan task mengikuti dependensi teknis dan prioritas operasional (petugas & admin dulu, nasabah mobile menyusul).
>
> **Referensi terkait:**
> - `04-api-contracts-and-standards.md` — format request/response & endpoint lengkap
> - `05-business-rules-sops.md` — aturan bisnis
> - `07-modules-and-features.md` — 17 modul sistem

---

## Ringkasan Fase

| Fase | Nama | Tujuan | Status |
|------|------|--------|--------|
| 0 | Foundation | Setup proyek, model, CRUD dasar | ✅ Selesai |
| 1 | MVP — Infrastruktur & Auth | Konfigurasi aman, auth, seed data, perbaikan dasar API | 🔲 Berikutnya |
| 2 | MVP — Logika Bisnis Inti | Validasi, workflow, transaksi atomik, permission per role | 🔲 |
| 3 | MVP — Operasional Harian | Setoran, penjemputan, penarikan, poin, pengaduan (end-to-end) | 🔲 |
| 4 | MVP — Monitoring & Laporan | Dashboard, laporan harian/bulanan, stok gudang | 🔲 |
| 5 | MVP Lengkap — Governance | Audit log, pengaturan institusi, role pemerintah, koreksi data | 🔲 |
| 6 | Kualitas & Dokumentasi | Testing, OpenAPI, error handling standar | 🔲 |
| 7 | Production Ready | Keamanan, deployment, backup, monitoring | 🔲 |
| 8 | Post-MVP | Peningkatan & optimasi jangka panjang | 🔲 |

### Cakupan 17 Modul Backend

| No | Modul | Fase Target |
|----|-------|-------------|
| 1 | Manajemen Akses & Pengguna | Fase 1–2 |
| 2 | Autentikasi & Akun Nasabah | Fase 1 |
| 3 | Profil & Kartu Digital (API data) | Fase 1 |
| 4 | Informasi & Edukasi Sampah | Fase 1 (seed) |
| 5 | Katalog & Harga Sampah | Fase 1–2 |
| 6 | Setor Sampah Langsung | Fase 2–3 |
| 7 | Penjemputan Sampah | Fase 2–3 |
| 8 | Penimbangan & Verifikasi | Fase 2 (bagian setoran) |
| 9 | Saldo & Riwayat Transaksi | Fase 2–3 |
| 10 | Penarikan Saldo | Fase 2–3 |
| 11 | Poin & Reward | Fase 2–3 |
| 12 | Stok Gudang | Fase 2–4 |
| 13 | Penjualan ke Mitra | Fase 2–3 |
| 14 | Pengaduan Nasabah | Fase 2–3 |
| 15 | Dashboard & Monitoring | Fase 4 |
| 16 | Laporan & Ekspor Data | Fase 4–5 |
| 17 | Pengaturan Sistem & Audit Log | Fase 5 |

### Gap Kode vs Dokumen (perlu ditangani)

| Item | Kondisi Saat Ini | Target |
|------|------------------|--------|
| Auth URL | `/api/auth/login/` | Standarkan & dokumentasikan (bukan `/api/token/`) |
| Role `pemerintah` | Belum ada di model User | Tambah role read-only untuk Pemerintah Distrik |
| Status `dalam_perjalanan` | Belum ada di model Penjemputan | Tambah ke STATUS_CHOICES |
| Field `tindak_lanjut` | Belum ada di model Pengaduan | Tambah field TextField |
| Field `jenis_pengaduan` | Belum ada | Tambah choices (7 jenis dari SOP) |
| Pagination | Belum dikonfigurasi global | PageNumberPagination 20/halaman |
| Error format | Format DRF default | JSON Envelope error (lihat `04` §3) |
| `transaction.atomic()` | Belum dipakai | Wajib untuk semua operasi saldo/stok/poin |
| `SECRET_KEY` | Hardcoded | Dari environment variable |
| `TIME_ZONE` | UTC | `Asia/Jayapura` (WIT) |
| Seed data | Belum ada | Management command kategori & reward |
| `views.py` | Import `permissions` hilang | Perbaiki bug |

---

## Fase 0: Foundation ✅ Selesai

### 0.1 Project Setup ✅
- [x] Create Django project (`core/`)
- [x] Create `api` app
- [x] Configure `settings.py` (DB, CORS, JWT, DRF)
- [x] Create Dockerfile & docker-compose.yml
- [x] Create `.env.example`
- [x] Install dependencies: DRF, simplejwt, django-filter, cors-headers, drf-spectacular, psycopg2

### 0.2 Database Models ✅
- [x] `User` (extends AbstractUser) — role, saldo, poin
- [x] `KategoriSampah`
- [x] `TransaksiSetoran` + `DetailSetoran`
- [x] `Penjemputan` (status workflow dasar)
- [x] `PenarikanSaldo`
- [x] `Reward` + `PenukaranPoin`
- [x] `MitraPengepul` + `PenjualanMitra`
- [x] `Pengaduan`
- [x] Run initial migrations

### 0.3 Core API Setup ✅
- [x] Serializers untuk semua model
- [x] ViewSets untuk semua model
- [x] URL routing dengan DefaultRouter
- [x] Custom permissions: `IsAdminOrKoordinator`, `IsPetugasOrAdmin`, `IsOwnerOrAdmin`
- [x] JWT auth endpoints (`/api/auth/login/`, `/api/auth/refresh/`)
- [x] drf-spectacular schema config
- [x] Health check endpoint (`/health/`)

---

## Fase 1: MVP — Infrastruktur & Auth

> **Tujuan:** Backend siap dipakai tim frontend dengan konfigurasi aman, auth stabil, dan data awal terisi.

### 1.1 Konfigurasi & Keamanan Dasar ✅
- [x] Pindahkan `SECRET_KEY` ke environment variable (wajib production)
- [x] Tambah `python-dotenv` atau load `.env` di `settings.py`
- [x] Set `TIME_ZONE = 'Asia/Jayapura'` dan `USE_TZ = True`
- [x] Set `ALLOWED_HOSTS` dari environment variable
- [x] Konfigurasi `SIMPLE_JWT` — access token 24 jam (sesuai constraint)
- [x] Tambah `restart: unless-stopped` di `docker-compose.yml` (dev convenience)
- [x] Tambah healthcheck Postgres di `docker-compose.yml`

### 1.2 Standar API Response — JSON Envelope ✅
- [x] Buat `api/utils/response.py` — helper `success_response()`, `error_response()`
- [x] Buat `api/utils/pagination.py` — pagination → `meta.pagination`
- [x] Buat `api/utils/exception_handler.py` — wrap semua error ke envelope
- [x] Buat `api/utils/renderers.py` — custom JSON renderer untuk envelope sukses
- [x] Konfigurasi global pagination: 20/halaman, max 100
- [x] Konfigurasi global ordering: `OrderingFilter`
- [x] Konfigurasi global search: `SearchFilter` pada endpoint user
- [x] Setiap response wajib punya: `success`, `status_code`, `message`, `data`, `meta`
- [x] `meta` wajib berisi: `timestamp` (ISO 8601 WIT), `request_id`
- [x] Standarkan format datetime ISO 8601 dengan timezone WIT di response

### 1.3 Autentikasi & Registrasi (Modul 2) ✅
- [x] Verifikasi `POST /api/auth/login/` — return access + refresh token
- [x] Verifikasi `POST /api/auth/refresh/` — refresh access token
- [x] Validasi registrasi: username unik, password min 6 karakter
- [x] Registrasi nasabah: `POST /api/users/` — role default `nasabah`, saldo/poin = 0
- [x] Endpoint `GET /api/auth/me/` — profil user yang sedang login (tanpa perlu tahu ID)
- [x] Return role di response login/me untuk kebutuhan redirect frontend

### 1.4 Manajemen Pengguna (Modul 1) ✅
- [x] Perbaiki bug import `permissions` di `views.py`
- [x] `GET /api/users/` — filter `?role=`, `?is_active=`, search `?search=`
- [x] `PATCH /api/users/{id}/` — nasabah hanya edit profil sendiri
- [x] Admin bisa create user petugas/admin/koordinator (bukan via registrasi publik)
- [x] Sembunyikan field `password` di response (sudah write_only, verifikasi)
- [x] Validasi: nasabah tidak bisa ubah `role`, `saldo`, `poin` via PATCH

### 1.5 Seed Data (Modul 4–5) ✅
- [x] Buat management command `seed_data`:
  - [x] 8 kategori sampah (PET, Gelas Plastik, Kardus, Kertas, Aluminium, Besi, Kaca, Jelantah)
  - [x] 4 reward default (Pulsa, Bibit, Sembako, Alat Kebersihan)
  - [x] 1 user admin default (untuk development)
- [x] Dokumentasikan cara menjalankan seed di README

### 1.6 Kategori Sampah (Modul 4–5) ✅
- [x] `GET /api/waste-categories/` — public, tanpa auth
- [x] `GET /api/waste-categories/{id}/` — public
- [x] Admin CRUD kategori — permission `IsAdminOrKoordinator`
- [x] Response include `stok_terkini_kg` untuk monitoring admin

---

## Fase 2: MVP — Logika Bisnis Inti

> **Tujuan:** Semua aturan bisnis SOP diterapkan di backend dengan integritas data terjaga.

### 2.1 Integritas Data Transaksional
- [x] Bungkus semua operasi saldo/stok/poin dalam `transaction.atomic()`
- [x] Gunakan `select_for_update()` saat update saldo nasabah (cegah race condition)
- [x] Tambah validasi saldo tidak boleh negatif setelah operasi
- [x] Tambah validasi stok tidak boleh negatif setelah penjualan

### 2.2 Transaksi Setoran (Modul 6, 8, 9)
- [x] Validasi: minimal **1 kg** per detail setoran
- [x] Validasi: nasabah exists, `is_active=True`, role=`nasabah`
- [x] Validasi: petugas role=`petugas` atau `admin`
- [x] Auto-hitung `harga_saat_itu` dari `KategoriSampah.harga_beli_per_kg` (jangan andalkan client)
- [x] Auto-hitung `subtotal = berat_kg × harga_saat_itu`
- [x] Auto-hitung `total_nilai` dari sum details
- [x] Side effect atomik: +saldo, +poin (`floor(total/1000)`), +stok per kategori
- [x] Permission create: `IsPetugasOrAdmin` (bukan nasabah)
- [x] Serializer read: return nested `details` pada GET (saat ini write_only)
- [x] Filter: `?nasabah=`, `?tanggal_after=`, `?tanggal_before=`
- [x] Ordering: `?ordering=-tanggal`

### 2.3 Penjemputan Workflow (Modul 7)
- [x] Tambah status `dalam_perjalanan` ke model (migration)
- [x] Validasi create: estimasi_berat >= **5 kg**
- [x] Validasi create: jadwal minimal **H+1** (tidak boleh hari ini atau masa lalu)
- [x] Validasi create: nasabah hanya bisa ajukan untuk diri sendiri
- [x] Implementasi state machine transisi status:
  - `menunggu` → `disetujui` | `ditolak` (admin)
  - `disetujui` → `dijadwalkan` (admin, assign petugas)
  - `dijadwalkan` → `dalam_perjalanan` (petugas)
  - `dalam_perjalanan` → `dijemput` (petugas)
  - `dijemput` → `selesai` (petugas, setelah input setoran)
- [x] Tolak transisi status yang tidak valid (return 409 Conflict)
- [x] Hanya admin yang assign `petugas` dan approve/reject
- [x] Petugas hanya update status penjemputan yang ditugaskan kepadanya
- [x] Filter: `?status=`, `?nasabah=`, `?petugas=`

### 2.4 Penarikan Saldo (Modul 10)
- [x] Validasi create: nominal >= **Rp50.000**
- [x] Validasi create: saldo nasabah >= nominal
- [x] Validasi create: tidak ada penarikan `menunggu` lain untuk nasabah yang sama
- [x] Side effect: kurangi saldo saat status → `selesai` (sudah ada, perbaiki dengan atomic)
- [x] Prevent double processing: tolak update jika sudah `selesai`
- [x] Permission approve: admin/koordinator only
- [x] Filter: `?status=`, `?nasabah=`

### 2.5 Penukaran Poin (Modul 11)
- [x] Validasi create: poin nasabah >= `reward.poin_dibutuhkan`
- [x] Validasi create: `reward.stok > 0`
- [x] Side effect atomik saat `selesai`: kurangi poin nasabah, kurangi stok reward
- [x] Prevent double processing
- [x] Permission approve: admin only

### 2.6 Penjualan Mitra & Stok (Modul 12–13)
- [x] Validasi: `stok_terkini_kg >= berat_jual_kg`
- [x] Auto-hitung `total_penjualan = berat_jual_kg × harga_jual_per_kg`
- [x] Side effect atomik: kurangi stok kategori
- [x] CRUD mitra pengepul — admin/koordinator
- [x] Mitra tidak punya akun login (hanya data referensi)

### 2.7 Pengaduan (Modul 14)
- [x] Tambah field `tindak_lanjut` (TextField, blank) ke model — migration
- [x] Tambah field `jenis_pengaduan` (choices, 7 jenis dari SOP) — migration
- [x] Nasabah create pengaduan → status `terbuka`
- [x] Admin update `tindak_lanjut` + status `ditutup`
- [x] Nasabah hanya lihat pengaduan sendiri
- [x] Filter: `?status=`, `?jenis_pengaduan=`

### 2.8 Permission & Queryset per Role
- [x] Nasabah: queryset difilter ke data milik sendiri (transaksi, penjemputan, saldo, pengaduan)
- [x] Petugas: bisa input setoran, update penjemputan yang ditugaskan
- [x] Admin: full access operasional
- [x] Koordinator: read-all + approve tertentu
- [x] Tambah role `pemerintah` — read-only dashboard & laporan
- [x] Tambah permission class `IsPemerintahReadOnly`

---

## Fase 3: MVP — Operasional Harian (End-to-End)

> **Tujuan:** Semua alur operasional bank sampah bisa jalan dari API tanpa workaround.

### 3.1 Alur Setor Langsung (SOP B.1)
- [x] Petugas scan/cari nasabah → input setoran → saldo & poin terupdate
- [x] Response setoran include bukti digital (id, tanggal, detail, total)
- [x] Endpoint `GET /api/deposits/{id}/` — detail lengkap untuk bukti

### 3.2 Alur Penjemputan (SOP B.2)
- [x] Nasabah ajukan → admin approve → assign petugas → petugas update status → selesai
- [x] Endpoint action: `POST /api/pickups/{id}/approve/`
- [x] Endpoint action: `POST /api/pickups/{id}/reject/`
- [x] Endpoint action: `POST /api/pickups/{id}/assign/` (body: `petugas_id`)
- [x] Endpoint action: `POST /api/pickups/{id}/update-status/` (body: `status`)

### 3.3 Alur Penarikan (SOP A.3)
- [x] Nasabah ajukan → admin approve manual → status selesai → saldo berkurang
- [x] Endpoint action: `POST /api/withdrawals/{id}/approve/`
- [x] Endpoint action: `POST /api/withdrawals/{id}/reject/` (opsional, kembalikan jika perlu)

### 3.4 Alur Penukaran Poin (SOP A.4)
- [x] Nasabah pilih reward → admin verifikasi → serahkan reward → approve
- [x] Endpoint action: `POST /api/reward-redemptions/{id}/approve/`

### 3.5 Riwayat Transaksi Gabungan (Modul 9)
- [x] `GET /api/activity/` — gabungan setoran + penarikan + penukaran untuk nasabah login
- [x] Query param: `?jenis=setoran|penarikan|poin`, `?page=`, `?ordering=-tanggal`
- [x] Response format standar dengan `type` field per item

### 3.6 Profil & Kartu Digital (Modul 3)
- [x] `GET /api/auth/me/` include data QR: `{ id, nama_lengkap, no_hp }`
- [x] `PATCH /api/auth/me/` — update profil tanpa ubah saldo/poin/role

### 3.7 Reward Katalog (Modul 11)
- [x] `GET /api/rewards/` — public list
- [x] Admin CRUD reward
- [x] Response include `stok` dan `poin_dibutuhkan`

---

## Fase 4: MVP — Monitoring & Laporan

> **Tujuan:** Admin, koordinator, dan pemerintah distrik bisa memantau program via data agregat.

### 4.1 Dashboard API (Modul 15)
- [x] `GET /api/dashboard/overview/`
  - total_nasabah, nasabah_aktif_30_hari
  - total_sampah_kg, total_nilai_setoran
  - total_penarikan, total_penukaran_poin
  - penjemputan_menunggu, pengaduan_terbuka
  - stok_per_kategori (array)
- [x] `GET /api/dashboard/deposit-chart/?bulan=6&tahun=2026`
  - data per hari/minggu untuk chart
- [x] `GET /api/dashboard/recent-activity/?limit=10`
  - 10 transaksi terbaru (setoran, penarikan, penjemputan)
- [x] Permission: admin, koordinator, pemerintah (read-only)

### 4.2 Laporan API (Modul 16)
- [x] `GET /api/reports/daily/?tanggal=2026-07-07`
  - jumlah_transaksi, total_setoran, total_penarikan, tonase_per_jenis
- [x] `GET /api/reports/weekly/?minggu=27&tahun=2026`
  - rekap mingguan, nasabah_baru, tonase_per_jenis
- [x] `GET /api/reports/monthly/?bulan=7&tahun=2026`
  - laporan lengkap sesuai format SOP (lihat `09-data-dictionary.md` H.1)
- [x] `GET /api/reports/waste/?start=2026-07-01&end=2026-07-31`
  - tonase dan nilai per kategori per periode
- [x] `GET /api/reports/evaluation/?start=&end=` — data agregat untuk evaluasi program
- [x] Permission: admin, koordinator, pemerintah

### 4.3 Stok Gudang (Modul 12)
- [x] `GET /api/inventory/` — ringkasan stok semua kategori
- [x] `GET /api/inventory/{kategori_id}/history/` — riwayat perubahan stok (post-MVP jika perlu model terpisah)

---

## Fase 5: MVP Lengkap — Governance

> **Tujuan:** Memenuhi persyaratan transparansi, audit, dan pengaturan institusi.

### 5.1 Audit Log (Modul 17)
- [ ] Buat model `AuditLog`: user, action, model_name, object_id, changes (JSON), timestamp, ip_address
- [ ] Catat otomatis via Django signals untuk: User, TransaksiSetoran, PenarikanSaldo, KategoriSampah, Pengaduan
- [ ] `GET /api/audit-log/` — admin only, filter `?user=`, `?model=`, `?date_after=`
- [ ] Koreksi data transaksi: hanya admin, wajib tercatat di audit log

### 5.2 Pengaturan Institusi (Modul 17)
- [ ] Buat model `PengaturanInstitusi` (singleton): nama, alamat, kontak, logo_url, jam_operasional, pengumuman
- [ ] `GET /api/settings/` — public (untuk tampilan mobile)
- [ ] `PATCH /api/settings/` — admin only
- [ ] `GET /api/pengumuman/` — list pengumuman aktif (untuk mobile)

### 5.3 Riwayat Harga (Modul 5 — opsional MVP)
- [ ] Buat model `RiwayatHarga`: kategori, harga_lama, harga_baru, tanggal_berlaku, diubah_oleh
- [ ] Auto-catat saat admin ubah `harga_beli_per_kg`
- [ ] `GET /api/waste-categories/{id}/price-history/`

### 5.4 Role Pemerintah Distrik
- [ ] Tambah role `pemerintah` ke User.ROLE_CHOICES
- [ ] Permission read-only untuk dashboard & laporan
- [ ] Tidak bisa create/update/delete data operasional

### 5.5 Kebijakan Data Pribadi (UU PDP)
- [ ] Endpoint consent saat registrasi: field `setuju_kebijakan_data: true` (required)
- [ ] Dokumentasikan data yang disimpan dan retensi (5 tahun)
- [ ] Enkripsi data sensitif (NIK) — evaluasi field-level encryption post-MVP

---

## Fase 6: Kualitas & Dokumentasi

> **Tujuan:** Backend teruji, terdokumentasi, dan siap diintegrasikan tim frontend.

### 6.1 Unit & Integration Tests
- [ ] Setup `pytest-django` + `factory-boy`
- [ ] Test registrasi nasabah (success, duplicate username, password pendek)
- [ ] Test JWT auth (login, refresh, expired token, invalid credentials)
- [ ] Test transaksi setoran (success, min 1kg, saldo+poin+stok update)
- [ ] Test penjemputan (create, status transitions, invalid transition → 409)
- [ ] Test penarikan saldo (min 50rb, saldo cukup, double approve)
- [ ] Test penukaran poin (poin cukup, stok habis)
- [ ] Test penjualan mitra (stok cukup, stok habis)
- [ ] Test permissions semua role (nasabah, petugas, admin, koordinator, pemerintah)
- [ ] Test race condition saldo (concurrent requests)
- [ ] Target coverage: minimal 80% untuk business logic

### 6.2 API Documentation (OpenAPI)
- [ ] Tambah `help_text` ke semua serializer fields
- [ ] Tambah tags drf-spectacular per modul (Auth, Users, Transaksi, dll.)
- [ ] Dokumentasikan semua error response di schema
- [ ] Verifikasi Swagger UI di `/api/docs/` render semua endpoint
- [ ] Export OpenAPI JSON ke repo untuk referensi frontend (`/api/schema/`)

### 6.3 Error Handling
- [ ] Custom exception handler mengembalikan JSON Envelope error (`success: false`, `code`, `errors`)
- [ ] Custom renderer mengembalikan JSON Envelope sukses (`success: true`, `data`, `meta`)
- [ ] Mapping error bisnis ke kode yang konsisten (lihat `04` §3.7)
- [ ] Logging error ke console (dev) dan file/Sentry (prod)

---

## Fase 7: Production Ready

> **Tujuan:** Backend siap deploy ke server Webekspres dengan keamanan dan reliabilitas production.

### 7.1 Keamanan
- [ ] `DEBUG=False` di production
- [ ] `SECRET_KEY` unik per environment
- [ ] Rate limiting: `10/minute` pada `/api/auth/login/` (django-ratelimit atau DRF throttle)
- [ ] Rate limiting: `100/hour` per user pada endpoint write
- [ ] HTTPS wajib (SSL termination di Nginx)
- [ ] `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF` config production
- [ ] CORS: whitelist domain production only
- [ ] Validasi input: sanitasi, max length enforcement

### 7.2 Deployment
- [ ] Ganti `runserver` dengan **Gunicorn** di Dockerfile production
- [ ] Tambah **Nginx** reverse proxy di docker-compose production
- [ ] Static files config (jika ada upload logo/bukti)
- [ ] Media files: storage lokal atau S3-compatible
- [ ] Environment separation: `.env.development`, `.env.production`
- [ ] CI/CD pipeline: lint → test → build → deploy (GitHub Actions)

### 7.3 Backup & Recovery
- [ ] Script backup harian: `pg_dump` → file terenkripsi
- [ ] Script backup mingguan: full backup + retensi 30 hari
- [ ] Backup disimpan terpisah dari server utama
- [ ] Dokumentasi prosedur restore
- [ ] Test restore minimal 1x sebelum go-live

### 7.4 Monitoring & Logging
- [ ] Structured logging (JSON format)
- [ ] Integrasi Sentry untuk error tracking
- [ ] Health check endpoint dengan status DB: `GET /health/` → `{ status, database, version }`
- [ ] Uptime monitoring (external ping ke `/health/`)

### 7.5 Performance
- [ ] Database indexes: `User.role`, `TransaksiSetoran.tanggal`, `Penjemputan.status`, `Pengaduan.status`
- [ ] `select_related` / `prefetch_related` pada queryset yang heavy
- [ ] Connection pooling PostgreSQL (pgBouncer atau Django CONN_MAX_AGE)
- [ ] Load test dasar: 50 concurrent users (locust atau k6)

---

## Fase 8: Post-MVP & Peningkatan

> **Tujuan:** Fitur tambahan setelah go-live operasional.

### 8.1 Fitur Tambahan
- [ ] Export laporan ke Excel server-side (`openpyxl`)
- [ ] Email notifikasi admin (laporan harian, penjemputan baru)
- [ ] Push notification trigger API (untuk integrasi FCM dari mobile)
- [ ] Notifikasi in-app: model `Notifikasi` + endpoint list/mark-read
- [ ] Bulk import nasabah via CSV/Excel
- [ ] Field upload foto KTP (FileField + storage)
- [ ] Bukti transaksi digital PDF (weasyprint atau reportlab)
- [ ] Kedaluwarsa poin otomatis (1 tahun) — scheduled task
- [ ] Transfer bank / e-wallet metadata pada penarikan (tanpa payment gateway)

### 8.2 Optimasi & Skalabilitas
- [ ] Redis cache untuk dashboard overview
- [ ] Celery + Redis untuk background jobs (backup, export, email)
- [ ] API versioning: `/api/v1/` → `/api/v2/` saat breaking change
- [ ] Read replica PostgreSQL (jika traffic meningkat)
- [ ] CDN untuk media files

### 8.3 Yang TIDAK BOLEH Diimplementasikan (System Constraints)
- [ ] ❌ Payment gateway otomatis (Midtrans, Xendit, dll.)
- [ ] ❌ GPS live tracking penjemputan
- [ ] ❌ Integrasi timbangan digital / barcode scanner fisik
- [ ] ❌ Integrasi API Dukcapil
- [ ] ❌ Multi-tenant (banyak bank sampah independen)
- [ ] ❌ Login untuk mitra/pengepul

---

## Urutan Pengerjaan Rekomendasi (Sprint)

### Sprint 1 (Minggu 1) — Fase 1
1.1 Konfigurasi & keamanan dasar
1.2 Standar API response
1.3 Auth & registrasi
1.5 Seed data

### Sprint 2 (Minggu 2) — Fase 2.1–2.2
2.1 Integritas transaksional
2.2 Transaksi setoran lengkap

### Sprint 3 (Minggu 3) — Fase 2.3–2.5
2.3 Penjemputan workflow
2.4 Penarikan saldo
2.5 Penukaran poin

### Sprint 4 (Minggu 4) — Fase 2.6–3
2.6–2.8 Penjualan, pengaduan, permissions
3.1–3.7 Alur end-to-end

### Sprint 5 (Minggu 5) — Fase 4
4.1 Dashboard API
4.2 Laporan API
4.3 Stok gudang

### Sprint 6 (Minggu 6) — Fase 5–6
5.1–5.5 Governance
6.1–6.3 Testing & dokumentasi

### Sprint 7 (Minggu 7) — Fase 7
7.1–7.5 Production ready

### Post-Launch — Fase 8
Sesuai kebutuhan operasional dan feedback pengguna.

---

## Definisi "Selesai" per Tahap

| Tahap | Kriteria Selesai |
|-------|------------------|
| **MVP** | Fase 1–4 selesai; web admin bisa operasional penuh |
| **MVP Lengkap** | Fase 5 selesai; audit log & pengaturan aktif |
| **Production Ready** | Fase 6–7 selesai; deploy ke staging, UAT lulus |
| **Go-Live** | Production deploy + backup aktif + monitoring aktif |
| **Post-MVP** | Fase 8 berjalan iteratif berdasarkan feedback |
