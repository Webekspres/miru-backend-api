# 08 — Task List: Backend Development Roadmap

> **Dokumen ini** adalah roadmap pengembangan backend MIRU Bank Sampah.
> Setiap item pengembangan lanjutan dicatat hanya jika tercantum di dokumen persyaratan
> (Proposal, Jawaban Persyaratan, SOP, Business Rules, Modules, Constraints).
>
> **Referensi terkait:**
> - `04-api-contracts-and-standards.md`
> - `05-business-rules-sops.md`
> - `06-system-constraints.md`
> - `07-modules-and-features.md`
> - `11-security-and-privacy.md` — **pedoman keamanan & privasi (kanonik)**
> - `Jawaban_Persyaratan_MIRU_Bank_Sampah.md`
> - `Proposal Bank sampah - Untuk Klien Pak Arfan.md`

---

## Ringkasan Fase

| Fase | Nama | Tujuan | Status |
|------|------|--------|--------|
| 0–6 | MVP → Governance & QA | Model, SOP bisnis, dashboard, audit, test, OpenAPI | ✅ Selesai |
| 7 | Production Ready | Keamanan, deploy, backup, monitoring | 🔲 Aktif |
| 8 | Pengembangan Lanjutan | Fitur pasca-MVP dari dokumen persyaratan | 🔲 Post-MVP |
| 9 | Out of Scope | Larangan sistem / butuh addendum kontrak | ⛔ Tidak dikerjakan |

### Cakupan 17 Modul Backend

| No | Modul | Status MVP | Pengembangan lanjutan |
|----|-------|------------|------------------------|
| 1 | Manajemen Akses & Pengguna | ✅ | Bulk import nasabah |
| 2 | Autentikasi & Akun Nasabah | ✅ | Lupa password, (opsional) verifikasi HP/email |
| 3 | Profil & Kartu Digital | ✅ | Foto KTP + enkripsi |
| 4 | Informasi & Edukasi Sampah | ✅ (kategori seed) | API konten artikel edukasi |
| 5 | Katalog & Harga Sampah | ✅ | Kebijakan harga H-3 |
| 6 | Setor Sampah Langsung | ✅ | PDF bukti |
| 7 | Penjemputan Sampah | ✅ | Wilayah + kuota 2×/minggu; Maps sederhana |
| 8 | Penimbangan & Verifikasi | ✅ | — |
| 9 | Saldo & Riwayat Transaksi | ✅ | Notifikasi FCM/WA/email |
| 10 | Penarikan Saldo | ✅ | Tanda terima PDF; metadata e-wallet sudah ada |
| 11 | Poin & Reward | ✅ | Kedaluwarsa poin 1 tahun |
| 12 | Stok Gudang | ✅ | — |
| 13 | Penjualan ke Mitra | ✅ | — |
| 14 | Pengaduan Nasabah | ✅ | — |
| 15 | Dashboard & Monitoring | ✅ | Cache; wilayah teraktif |
| 16 | Laporan & Ekspor Data | ✅ | Excel server-side; evaluasi kendala |
| 17 | Pengaturan Sistem & Audit Log | ✅ | Arsip retensi 5 tahun |

---

# BAGIAN A — BELUM SELESAI (prioritas atas)

---

## Fase 7: Production Ready

> **Tujuan:** Backend siap deploy ke server Webekspres.
> **Sumber:** Jawaban Persyaratan §6.5; Constraints §7–8; Timeline go-live;
> **`11-security-and-privacy.md`** (checklist go-live §12).

### 7.1 Keamanan API & Konfigurasi
> Detail aturan: `11-security-and-privacy.md` §3–5.

- [x] `DEBUG=False` di production — dari env var `DEBUG`
- [x] `SECRET_KEY` unik per environment — dari env var
- [x] Validasi input: sanitasi, max length — via DRF serializers
- [x] Password write_only; JWT auth; permission + queryset per role *(MVP)*
- [x] Ledger atomic + `select_for_update` *(keamanan finansial — MVP)*
- [x] Audit log perubahan kritis *(MVP)*
- [x] Consent `setuju_kebijakan_data` saat registrasi *(MVP)*
- [x] Rate limiting: `10/minute` pada `/api/auth/login/` — `LoginAnonRateThrottle`
- [x] Rate limiting: `100/hour` per user pada endpoint write — `WriteUserRateThrottle` global
- [x] HTTPS wajib (SSL termination di Nginx) — `SECURE_PROXY_SSL_HEADER` + `SECURE_SSL_REDIRECT`
- [x] `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` — di `if not DEBUG:`
- [x] `SECURE_HSTS_SECONDS` setelah HTTPS stabil — 31536000 (1 tahun)
- [x] `ALLOWED_HOSTS` production ketat dari env — sudah dari MVP
- [x] CORS: whitelist origin web-admin + domain resmi saja (**bukan** `*`) — default = `bool(DEBUG)`
- [x] Pastikan tidak ada stack trace / secret di response production — `DEBUG=False` + custom exception handler
- [x] Verifikasi test permission: nasabah tidak akses data milik orang lain — 6 test isolasi di `test_role_permissions.py`

### 7.2 Deployment
- [x] Ganti `runserver` dengan **Gunicorn** di Dockerfile production
- [x] Tambah **Nginx** reverse proxy di docker-compose production
- [x] Static files config — `STATIC_ROOT`, `STATIC_URL` di settings.py
- [x] Media files: storage lokal — `MEDIA_ROOT`, `MEDIA_URL`; S3 opsional (Fase 8)
- [x] Environment separation: `docker-compose.production.yml` override tanpa host mount
- [x] `.env*` di gitignore; `.env.example` tanpa nilai rahasia — sudah MVP, diperbarui
- [x] CI/CD pipeline: `.github/workflows/ci.yml` — lint → test → build → deploy

### 7.3 Backup & Recovery
> **Sumber:** Jawaban §6.5.6; Constraints §7; Security §9.

- [x] Script backup harian: `pg_dump` → pipe ke GPG AES-256 (`scripts/backup.sh`)
- [x] Script backup mingguan: full backup + retensi 30 hari + rsync remote (`scripts/backup_weekly.sh`)
- [x] Backup disimpan terpisah — rsync ke REMOTE_HOST + dokumentasi di BACKUP.md
- [x] Dokumentasi prosedur restore + siapa yang berwenang — `BACKUP.md` + `scripts/restore.sh`
- [ ] Test restore minimal 1× sebelum go-live — **testing manual** (lihat BACKUP.md §7)

### 7.4 Monitoring & Logging
> **Sumber:** Security §8 — redact PII/token.

- [x] Health check: `GET /health/` → `{ status, database }`
- [x] Structured logging (JSON format) — `JSONFormatter` + `RequestLoggingMiddleware`
- [x] Redact password, token, NIK dari log — `PIIRedactFilter`
- [ ] Integrasi Sentry + scrub PII di `before_send` — **ditunda** (instruksi user)
- [x] Uptime monitoring (external ping ke `/health/`) — `scripts/healthcheck.sh`
- [x] Pantau spike 401 / 429 / 5xx — `RequestLoggingMiddleware` (WARNING/ERROR per status)

### 7.5 Performance
- [x] Database indexes (`User.role`, tanggal/status transaksi, dll.)
- [x] `select_related` / `prefetch_related` pada queryset heavy
- [x] Connection pooling PostgreSQL — `CONN_MAX_AGE=300` (env var, default 300s)
- [x] Load test dasar: ~50 concurrent users — `scripts/locustfile.py` (4 user classes)

---

## Fase 8: Pengembangan Lanjutan (pasca-MVP)

> **Tujuan:** Fitur tambahan setelah go-live, **hanya** yang tercantum di dokumen persyaratan.
> Bukan lingkup MVP.

### 8.1 Modul 4 — Konten edukasi sampah
> **Sumber:** Proposal §4 modul 4 (artikel edukasi); `07-modules` Web Admin “kelola konten (future)”.

- [x] Model konten edukasi (judul, isi/panduan, kategori terkait, aktif, urutan)
- [x] CRUD API — admin/koordinator
- [x] List/detail public (atau auth nasabah) untuk mobile
- [x] Seed konten awal dari panduan pemilahan (`09-data-dictionary`)

### 8.2 Modul 5 — Kebijakan perubahan harga H-3
> **Sumber:** Business Rules §G; Jawaban §6.2.4; Data dictionary catatan harga.

- [x] `tanggal_berlaku` wajib minimal H+3 dari saat penetapan
- [x] Tolak apply harga ke transaksi sebelum `tanggal_berlaku`
- [x] Auto-buat/hubungkan pengumuman perubahan harga ke nasabah
- [x] (Riwayat harga model sudah ada — perpanjang aturan bisnis)

### 8.3 Modul 7 — Wilayah layanan & kuota penjemputan
> **Sumber:** Business Rules §F/M; Jawaban §6.2.12–13; Data dictionary §K; Proposal modul 3/7.

- [x] Model/referensi wilayah layanan (kelurahan / RT-RW)
- [x] Validasi penjemputan hanya di wilayah terdaftar (tahap awal: sekitar kantor distrik)
- [x] Validasi frekuensi max **2× seminggu per wilayah** (selaras SOP final klien)
- [x] Field kelurahan/RT-RW pada User/nasabah (opsional di registrasi)
- [x] Agregat `wilayah_teraktif` di dashboard/evaluasi (kontrak API)

### 8.4 Modul 2 / 3 / 10 — Identitas, lupa password, bukti pencairan
> **Sumber:** Proposal §4 modul 2–3, 10; Jawaban §6.2.7, §6.3.4, §6.3.6;
> **`11-security-and-privacy.md`** §2, §7, §12 (pasca-MVP). 

- [x] Endpoint lupa password + reset token berumur pendek (email atau alur aman yang disepakati)
- [x] (Opsional) verifikasi nomor HP/email — hanya jika disepakati klien (Proposal modul 2)
- [x] Upload foto KTP (`FileField` + storage privat) untuk verifikasi penarikan besar
- [x] Validasi tipe/ukuran file upload; larang executable
- [x] Field-level encryption NIK / data KTP at-rest *(Jawaban §6.3.4)*
- [x] Threshold “penarikan besar” + wajib lampiran KTP
- [x] Akses unduh KTP/PDF **role-gated** (bukan URL publik terbuka)
- [x] Generate PDF tanda terima / bukti setoran & penarikan (weasyprint atau reportlab)
- [x] Metadata metode transfer bank / e-wallet pada penarikan (**tanpa** payment gateway)

### 8.5 Modul 11 — Masa berlaku poin 1 tahun
> **Sumber:** Business Rules §A.4; Jawaban §6.2.10.

- [x] Scheduled task kedaluwarsa poin otomatis (1 tahun)
- [x] Catat di audit log dan/atau notifikasi saat poin hangus
- [x] Endpoint/info sisa masa berlaku poin untuk nasabah (opsional)

### 8.6 Modul 9 / 16 — Notifikasi & laporan lanjutan
> **Sumber:** Jawaban §6.6.2 / §6.6.5; Proposal modul 9 & 16; Jawaban §6.3.9; Constraints §8;
> Security §11 (payload tanpa NIK/KTP).

- [x] Notifikasi in-app: model `Notifikasi` + endpoint list/mark-read
- [x] Trigger FCM (register device token milik user + kirim event: jemput, penarikan, pengumuman, harga)
- [x] Payload FCM/WA **tanpa** NIK, KTP, atau token *(FCM done; WA pending)*
- [ ] Integrasi WhatsApp Business API untuk konfirmasi setoran & penarikan *(Jawaban §6.6.2)*
- [x] Email transactional admin (penjemputan baru, ringkasan harian) *(Jawaban §6.5.5 / §6.6.5)*
- [x] Kredensial FCM / WA / SMTP hanya di env (bukan di repo)
- [x] Export laporan Excel server-side (`openpyxl`)
- [x] Laporan evaluasi: field kendala + rekomendasi tindak lanjut *(Proposal modul 16)*
- [x] Kebijakan retensi/arsip digital transaksi minimal 5 tahun *(Jawaban §6.3.9)*

### 8.7 Modul 7 — Integrasi peta sederhana
> **Sumber:** Jawaban §6.6.1; Constraints §5; Security §11 (API key di-restrict).

- [ ] Field koordinat opsional atau geocode alamat penjemputan
- [ ] Konfigurasi Maps API key di environment; restrict key (IP/referrer/bundle)
- [ ] Dokumentasikan batasan: tidak ada distance matrix / navigasi real-time

### 8.8 Operasional data & infrastruktur pendukung
> **Sumber:** Persyaratan data klien; dukungan Fase 8 notifikasi/backup; Constraints performa.

- [ ] Bulk import nasabah via CSV/Excel
- [ ] Celery + Redis untuk background jobs (backup, export, email, FCM)
- [ ] Redis cache untuk dashboard overview
- [ ] API versioning `/api/v1/` saat breaking change
- [ ] CDN untuk media files (jika traffic media naik)
- [ ] Read replica PostgreSQL (hanya jika traffic meningkat nyata)

### 8.9 Publikasi platform (dukungan backend)
> **Sumber:** Constraints §10; Jawaban §6.4 (Android prioritas, iOS menyusul).

- [ ] Pastikan CORS/HTTPS production siap untuk mobile release
- [ ] Endpoint privacy policy (sudah ada kerangka) — URL publik untuk Play Store

---

## Fase 9: Out of Scope / Larangan Sistem

> **Sumber:** `06-system-constraints.md`; Proposal §5 batasan.
> Item di bawah **tidak dikerjakan** kecuali ada addendum kontrak tertulis.

- [ ] ❌ Payment gateway otomatis (Midtrans, Xendit, dll.) — Jawaban §6.6.3 menyebut “tahap lanjut”, tetapi **dilarang** di Proposal §5.3 & Constraints
- [ ] ❌ GPS live tracking penjemputan
- [ ] ❌ Integrasi timbangan digital / barcode scanner fisik / printer auto
- [ ] ❌ Integrasi API Dukcapil
- [ ] ❌ Multi-tenant (banyak bank sampah independen)
- [ ] ❌ Login untuk mitra/pengepul

---

# BAGIAN B — ARSIP MVP (Selesai) — urutan bawah

> Fase 0–6 telah diimplementasikan. Dipertahankan sebagai catatan verifikasi.

---

## Fase 0: Foundation ✅

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

## Fase 1: MVP — Infrastruktur & Auth ✅

### 1.1 Konfigurasi & Keamanan Dasar ✅
- [x] `SECRET_KEY` dari environment variable
- [x] Load `.env` di `settings.py`
- [x] `TIME_ZONE = 'Asia/Jayapura'`, `USE_TZ = True`
- [x] `ALLOWED_HOSTS` dari environment
- [x] `SIMPLE_JWT` — access token 24 jam
- [x] `restart: unless-stopped` + healthcheck Postgres di docker-compose

### 1.2 Standar API Response — JSON Envelope ✅
- [x] `api/utils/response.py` — `success_response()`, `error_response()`
- [x] `api/utils/pagination.py` — `meta.pagination`
- [x] `api/utils/exception_handler.py` — wrap error ke envelope
- [x] `api/utils/renderers.py` — custom JSON renderer
- [x] Pagination global: 20/halaman, max 100
- [x] OrderingFilter + SearchFilter
- [x] Envelope: `success`, `status_code`, `message`, `data`, `meta`
- [x] `meta.timestamp` (ISO 8601 WIT), `meta.request_id`

### 1.3 Autentikasi & Registrasi (Modul 2) ✅
- [x] `POST /api/auth/login/` — access + refresh
- [x] `POST /api/auth/refresh/`
- [x] Validasi registrasi: username unik, password min 6
- [x] Registrasi nasabah: role default `nasabah`, saldo/poin = 0
- [x] `GET /api/auth/me/`
- [x] Role di response login/me

### 1.4 Manajemen Pengguna (Modul 1) ✅
- [x] Filter `?role=`, `?is_active=`, `?search=`
- [x] Nasabah hanya edit profil sendiri
- [x] Admin create user petugas/admin/koordinator
- [x] Password write_only
- [x] Nasabah tidak bisa ubah `role`, `saldo`, `poin` via PATCH

### 1.5 Seed Data (Modul 4–5) ✅
- [x] Management command `seed_data` — 8 kategori, 4 reward, admin default
- [x] Dokumentasi seed di README

### 1.6 Kategori Sampah (Modul 4–5) ✅
- [x] `GET /api/waste-categories/` public
- [x] Admin CRUD — `IsAdminOrKoordinator`
- [x] Response include `stok_terkini_kg`

---

## Fase 2: MVP — Logika Bisnis Inti ✅

### 2.1 Integritas Data Transaksional ✅
- [x] `transaction.atomic()` pada operasi saldo/stok/poin
- [x] `select_for_update()` saat update saldo
- [x] Validasi saldo & stok tidak negatif

### 2.2 Transaksi Setoran (Modul 6, 8, 9) ✅
- [x] Min 1 kg per detail; validasi nasabah/petugas
- [x] Auto `harga_saat_itu`, `subtotal`, `total_nilai`
- [x] Side effect: +saldo, +poin (`floor(total/1000)`), +stok
- [x] Nested `details` pada GET; filter & ordering

### 2.3 Penjemputan Workflow (Modul 7) ✅
- [x] Status `dalam_perjalanan`; estimasi ≥5 kg; jadwal H+1
- [x] State machine + 409 pada transisi invalid
- [x] Assign petugas admin-only; petugas update assigned

### 2.4 Penarikan Saldo (Modul 10) ✅
- [x] Min Rp50.000; saldo cukup; satu `menunggu` aktif
- [x] Debit saldo saat selesai; prevent double processing

### 2.5 Penukaran Poin (Modul 11) ✅
- [x] Validasi poin & stok reward; approve atomik

### 2.6 Penjualan Mitra & Stok (Modul 12–13) ✅
- [x] Validasi stok; auto total; kurangi stok; CRUD mitra (tanpa login)

### 2.7 Pengaduan (Modul 14) ✅
- [x] `tindak_lanjut`, `jenis_pengaduan` (7 choices); filter status/jenis

### 2.8 Permission & Queryset per Role ✅
- [x] Nasabah scoped; petugas/admin/koordinator; role `pemerintah` read-only
- [x] `IsPemerintahReadOnly` / monitor read-only

---

## Fase 3: MVP — Operasional Harian ✅

### 3.1–3.4 Alur E2E ✅
- [x] Setoran + bukti digital
- [x] Pickup actions: approve / reject / assign / update-status
- [x] Withdrawal approve / reject
- [x] Redemption approve

### 3.5 Riwayat Gabungan (Modul 9) ✅
- [x] `GET /api/activity/` — filter jenis, paginate, ordering

### 3.6 Profil & Kartu Digital (Modul 3) ✅
- [x] `/api/auth/me/` include data QR; PATCH profil aman

### 3.7 Reward Katalog (Modul 11) ✅
- [x] List public + admin CRUD; `stok`, `poin_dibutuhkan`

---

## Fase 4: MVP — Monitoring & Laporan ✅

### 4.1 Dashboard (Modul 15) ✅
- [x] `/api/dashboard/overview/`, `deposit-chart/`, `recent-activity/`

### 4.2 Laporan (Modul 16) ✅
- [x] daily / weekly / monthly / waste / evaluation

### 4.3 Stok Gudang (Modul 12) ✅
- [x] `/api/inventory/` + history per kategori

---

## Fase 5: MVP Lengkap — Governance ✅

### 5.1 Audit Log (Modul 17) ✅
- [x] Model `AuditLog` + signals; `GET /api/audit-log/`

### 5.2 Pengaturan Institusi (Modul 17) ✅
- [x] `PengaturanInstitusi`; `/api/settings/`; `/api/pengumuman/`

### 5.3 Riwayat Harga (Modul 5) ✅
- [x] Model `RiwayatHarga`; auto-catat; price-history endpoint

### 5.4 Role Pemerintah Distrik ✅
- [x] Role di choices; read-only dashboard & laporan

### 5.5 Kebijakan Data Pribadi (UU PDP) ✅
- [x] Consent `setuju_kebijakan_data` required saat registrasi
- [x] Dokumentasi retensi 5 tahun (dokumen)
- [ ] ~~Enkripsi NIK~~ → dipindah ke Fase 8.4 (belum diimplementasikan)

---

## Fase 6: Kualitas & Dokumentasi ✅

### 6.1 Tests ✅
- [x] ~21 file test (auth, deposits, pickups, withdrawals, permissions, dashboard, reports, audit, integrity, dll.)

### 6.2 OpenAPI ✅
- [x] Tags Spectacular; Swagger `/api/docs/`; schema `/api/schema/`

### 6.3 Error Handling ✅
- [x] Envelope error/sukses; kode error domain; logging

---

## Definisi "Selesai" per Tahap

| Tahap | Kriteria |
|-------|----------|
| **MVP** | Fase 0–4 selesai; web admin operasional |
| **MVP Lengkap** | Fase 5 selesai; audit & pengaturan aktif |
| **UAT / Production Ready** | Fase 6–7 selesai; deploy staging + backup + monitoring |
| **Go-Live** | Production deploy + backup aktif + monitoring aktif |
| **Pengembangan Lanjutan** | Fase 8 iteratif berdasarkan prioritas operasional & dokumen persyaratan |

---

## Urutan kerja disarankan (pasca-MVP)

1. **Fase 7** — Production Ready + checklist keamanan `11-security-and-privacy.md` §12 (blocker go-live)
2. **8.5** Poin expire + **8.2** Harga H-3 (aturan bisnis yang sudah tertulis)
3. **8.1** Edukasi konten + **8.3** Wilayah (melengkapi Modul 4 & 7)
4. **8.4** KTP/PDF/lupa password (keamanan data sensitif) + **8.6** FCM/WA/email
5. **8.7–8.8** Maps sederhana + infrastruktur async

## Indeks dokumen keamanan lintas repo

| Repo | Dokumen |
|------|---------|
| Backend (kanonik) | `.ai-steering/11-security-and-privacy.md` |
| Web Admin | `web-admin/.ai-steering/11-security-and-privacy.md` |
| Mobile | `mirumobileapp/.ai-steering/11-security-and-privacy.md` |
