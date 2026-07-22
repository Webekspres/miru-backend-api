# 08 — Task List: Backend Development Roadmap

> **Dokumen ini** adalah roadmap pengembangan backend MIRU Bank Sampah.
> **Urutan:** item **belum selesai di atas**; item **sudah selesai di bawah** (arsip).
>
> Setiap item pengembangan lanjutan hanya dari dokumen persyaratan
> (Proposal, Jawaban Persyaratan, SOP, Business Rules, Modules, Constraints)
> dan berada dalam **17 modul** sistem. MVP sudah selesai — Fase 7–8 adalah lingkup kerja aktif.
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
| 0–6 | MVP → Governance & QA | Model, SOP bisnis, dashboard, audit, test, OpenAPI | ✅ Selesai (arsip) |
| 7 | Production Ready | Keamanan, deploy, backup, monitoring | 🔲 Sisa go-live manual |
| 8 | Pengembangan Lanjutan | Fitur dari dokumen persyaratan dalam **17 modul** | 🔲 Sisa infrastruktur / WA / Maps |
| 9 | Out of Scope | Larangan sistem / butuh addendum kontrak | ⛔ Tidak dikerjakan |

> **Status proyek:** MVP (Fase 0–6) selesai. Hampir semua API Fase 8 fitur bisnis ✅.
> Kerja aktif backend = **sisa go-live Fase 7** + **sisa Fase 8** (WA, Maps, bulk import, job queue).
> Klien (Web Admin Fase 9 + Mobile Fase 8) harus di-wire ke API yang sudah ✅.
> **Tidak boleh** menambah fitur di luar 17 modul tanpa addendum.

### Cakupan 17 Modul Backend

| No | Modul | Status API | Sisa / catatan |
|----|-------|------------|----------------|
| 1 | Manajemen Akses & Pengguna | ✅ | Bulk import nasabah (belum) |
| 2 | Autentikasi & Akun Nasabah | ✅ | Lupa password ✅; verifikasi HP/email opsional ✅ |
| 3 | Profil & Kartu Digital | ✅ | KTP + enkripsi NIK ✅ |
| 4 | Informasi & Edukasi Sampah | ✅ | CRUD + list/detail edukasi ✅ |
| 5 | Katalog & Harga Sampah | ✅ | Kebijakan harga H-3 ✅ |
| 6 | Setor Sampah Langsung | ✅ | PDF bukti ✅ |
| 7 | Penjemputan Sampah | ✅ | Wilayah + kuota ✅; Maps koordinat (belum) |
| 8 | Penimbangan & Verifikasi | ✅ | — |
| 9 | Saldo & Riwayat Transaksi | ✅ | In-app + FCM ✅; WhatsApp (belum) |
| 10 | Penarikan Saldo | ✅ | PDF tanda terima + metadata metode ✅ |
| 11 | Poin & Reward | ✅ | Kedaluwarsa poin 1 tahun ✅ |
| 12 | Stok Gudang | ✅ | — |
| 13 | Penjualan ke Mitra | ✅ | — |
| 14 | Pengaduan Nasabah | ✅ | — |
| 15 | Dashboard & Monitoring | ✅ | Cache Redis (belum, opsional) |
| 16 | Laporan & Ekspor Data | ✅ | Excel server-side + evaluasi ✅ |
| 17 | Pengaturan Sistem & Audit Log | ✅ | Retensi 5 tahun ✅; privacy policy endpoint ✅ |

---

## Urutan kerja disarankan (lintas repo)

1. **Backend sisa go-live** — test restore backup; verifikasi CORS/HTTPS production + URL privacy policy publik.
2. **Web Admin Fase 9** — wire fitur ke API yang sudah ✅ (edukasi CRUD → harga H-3 → wilayah/RT-RW → PDF/KTP → laporan).
3. **Mobile Fase 8** — wire sisa UI ke API yang sudah ✅ (lupa password → RT/RW → banner harga → PDF/poin → FCM).
4. **Backend opsional** — WhatsApp, Maps koordinat, bulk import, Celery/Redis — sesuai prioritas operasional klien.
5. **Jangan** kerjakan Out of Scope tanpa addendum.

---

# BAGIAN A — BELUM SELESAI (prioritas atas)

> Hanya item `[ ]`. Detail cukup untuk dikerjakan tanpa menebak di luar 17 modul.

---

## Fase 7: Production Ready — sisa go-live

> **Tujuan:** Backend siap production Webekspres.
> **Sumber:** Jawaban §6.5; Constraints §7–8; `11-security-and-privacy.md` §12.
> Konfigurasi keamanan, Gunicorn/Nginx, CI, logging, index, load test — **sudah ✅** (lihat BAGIAN B).

### 7.3 Backup & Recovery — sisa

- [ ] **Test restore minimal 1× sebelum go-live**
  - Ikuti prosedur `BACKUP.md` §7 + `scripts/restore.sh`
  - Verifikasi: DB restore → `/health/` OK → login admin + 1 transaksi baca berhasil
  - Catat tanggal, siapa yang menjalankan, hasil lolos/gagal

### 7.4 Monitoring — ditunda (bukan blocker)

- [ ] **Integrasi Sentry + scrub PII di `before_send`** — **ditunda** (instruksi user)
  - Saat diaktifkan: jangan kirim NIK, token, password, isi KTP ke Sentry
  - Referensi: `11-security-and-privacy.md` §8

---

## Fase 8: Pengembangan Lanjutan — sisa

> Fitur bisnis Modul 2–7, 9–11, 16 hampir semua ✅ di BAGIAN B.
> Di bawah hanya yang **belum** diimplementasikan.

### 8.6 Modul 9 — Notifikasi WhatsApp (lanjutan channel)

> **Sumber:** Jawaban §6.6.2; Proposal modul 9; Security §11 (payload tanpa NIK/KTP).
> FCM + in-app + email admin sudah ✅.

- [ ] **Integrasi WhatsApp Business API** untuk konfirmasi setoran & penarikan
  - Event minimal: setoran berhasil; penarikan disetujui/ditolak
  - Payload **tanpa** NIK, nomor KTP lengkap, saldo penuh, atau token JWT
  - Kredensial hanya di env (`WA_*` / setara) — jangan commit ke repo
  - Fallback: jika WA gagal, in-app/FCM tetap jalan; log error tanpa PII
  - Dokumentasikan opt-in / nomor HP sumber (dari profil nasabah)

### 8.7 Modul 7 — Integrasi peta sederhana

> **Sumber:** Jawaban §6.6.1; Constraints §5; Security §11 (API key di-restrict).
> **Bukan** GPS live tracking armada.

- [ ] **Field koordinat opsional** pada penjemputan (atau geocode alamat → lat/lng)
  - Simpan di model/serializer penjemputan; boleh null jika alamat teks saja
  - Validasi rentang koordinat masuk akal (Papua / area layanan)
- [ ] **Konfigurasi Maps API key di environment**
  - Restrict key: IP server / referrer web-admin / bundle ID mobile
  - Jangan hardcode key di source
- [ ] **Dokumentasikan batasan** di kontrak/API docs
  - Tidak ada distance matrix, navigasi real-time, atau live tracking petugas

### 8.8 Modul 1 / 15 / infrastruktur pendukung

> **Sumber:** Persyaratan data klien; Constraints performa; dukungan notifikasi/backup.

#### Modul 1 — Bulk import nasabah

- [ ] **Bulk import nasabah via CSV/Excel**
  - Endpoint admin/koordinator; validasi baris (username unik, password policy, role = nasabah)
  - Batasi ukuran file; response envelope: sukses N / gagal M + detail baris error
  - Consent `setuju_kebijakan_data` harus eksplisit di template/import atau ditolak
  - Audit log: siapa import, jumlah, waktu
  - **Tidak** import role staff lewat endpoint yang sama tanpa guard ketat

#### Infrastruktur (dukungan modul 9/15/16 — bukan modul baru)

- [ ] **Celery + Redis** untuk background jobs
  - Antrean: email transactional, FCM batch, (nanti) WA, export berat, backup trigger
  - Worker di docker-compose production; retry + dead-letter sederhana
- [ ] **Redis cache** untuk dashboard overview (`/api/dashboard/overview/`)
  - TTL pendek; invalidate saat transaksi kritis jika feasible
- [ ] **API versioning `/api/v1/`** — hanya saat ada **breaking change** kontrak
  - Jangan rename path sekarang jika klien masih `/api/`
- [ ] **CDN untuk media files** — hanya jika traffic media/KTP/PDF naik nyata
- [ ] **Read replica PostgreSQL** — hanya jika traffic baca meningkat nyata

### 8.9 Publikasi platform (dukungan Modul 2 / Play Store)

> **Sumber:** Constraints §10; Jawaban §6.4. Endpoint `GET /api/privacy-policy/` sudah ada ✅.

- [ ] **Verifikasi CORS + HTTPS production** siap untuk mobile release
  - `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` whitelist domain web-admin + (jika perlu) origin tool
  - Cleartext tidak dipakai di production; SSL termination Nginx OK
- [ ] **URL publik privacy policy** untuk Play Store
  - Endpoint/kerangka sudah ada — pastikan domain HTTPS final + konten selaras kebijakan data
  - Berikan URL final ke tim mobile (Fase 7 Play Store)

---

## Fase 9: Out of Scope / Larangan Sistem

> **Sumber:** `06-system-constraints.md`; Proposal §5.
> **Tidak dikerjakan** kecuali addendum kontrak tertulis.

- [ ] ❌ Payment gateway otomatis (Midtrans, Xendit, dll.)
- [ ] ❌ GPS live tracking penjemputan
- [ ] ❌ Integrasi timbangan digital / barcode scanner fisik / printer auto
- [ ] ❌ Integrasi API Dukcapil
- [ ] ❌ Multi-tenant (banyak bank sampah independen)
- [ ] ❌ Login untuk mitra/pengepul

---

# BAGIAN B — SELESAI (arsip) — urutan bawah

> Dipertahankan sebagai catatan verifikasi. Jangan mengulang pekerjaan di sini.

---

## Fase 7 (selesai) — Production Ready ✅

### 7.1 Keamanan API & Konfigurasi ✅
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
- [x] `ALLOWED_HOSTS` production ketat dari env
- [x] CORS: whitelist origin (bukan `*`) — default longgar hanya di DEBUG
- [x] Tidak ada stack trace / secret di response production — `DEBUG=False` + custom exception handler
- [x] Test isolasi permission nasabah — `test_role_permissions.py`

### 7.2 Deployment ✅
- [x] Gunicorn di Dockerfile production
- [x] Nginx reverse proxy di docker-compose production
- [x] Static/media config (`STATIC_*`, `MEDIA_*`)
- [x] `docker-compose.production.yml` tanpa host mount
- [x] `.env*` di gitignore; `.env.example` tanpa rahasia
- [x] CI/CD `.github/workflows/ci.yml` — lint → test → build → deploy

### 7.3 Backup & Recovery (implementasi) ✅
- [x] Backup harian `scripts/backup.sh` — `pg_dump` → GPG AES-256
- [x] Backup mingguan `scripts/backup_weekly.sh` + retensi 30 hari + rsync
- [x] Dokumentasi `BACKUP.md` + `scripts/restore.sh`

### 7.4 Monitoring & Logging ✅
- [x] `GET /health/` → `{ status, database }`
- [x] Structured JSON logging + `RequestLoggingMiddleware`
- [x] Redact password, token, NIK — `PIIRedactFilter`
- [x] Uptime ping `scripts/healthcheck.sh`
- [x] Pantau spike 401 / 429 / 5xx di middleware

### 7.5 Performance ✅
- [x] Database indexes
- [x] `select_related` / `prefetch_related` pada queryset heavy
- [x] `CONN_MAX_AGE=300` (env)
- [x] Load test dasar Locust ~50 concurrent — `scripts/locustfile.py`

---

## Fase 8 (selesai) — Pengembangan Lanjutan fitur bisnis ✅

### 8.1 Modul 4 — Konten edukasi sampah ✅
- [x] Model `KontenEdukasi` (judul, isi, kategori terkait, aktif, urutan)
- [x] CRUD API admin/koordinator — `KontenEdukasiViewSet` `/api/edukasi/`
- [x] List/detail public (atau auth nasabah) untuk mobile
- [x] Seed konten awal dari panduan pemilahan

### 8.2 Modul 5 — Kebijakan perubahan harga H-3 ✅
- [x] `tanggal_berlaku` wajib minimal H+3 dari saat penetapan
- [x] Tolak apply harga ke transaksi sebelum `tanggal_berlaku`
- [x] Auto-buat/hubungkan pengumuman perubahan harga ke nasabah
- [x] Riwayat harga diperpanjang aturan bisnis

### 8.3 Modul 7 — Wilayah layanan & kuota penjemputan ✅
- [x] Model `WilayahLayanan` (kelurahan / RT-RW)
- [x] Validasi penjemputan hanya di wilayah terdaftar
- [x] Validasi frekuensi max **2× seminggu per wilayah**
- [x] Field kelurahan/RT-RW pada User/nasabah
- [x] Agregat `wilayah_teraktif` di dashboard/evaluasi
- [x] Filter list `?status=` dan `?status__in=`
- [x] Alur status: menunggu → disetujui → dijadwalkan (+assign petugas) → … → selesai/ditolak
- [x] Notifikasi in-app ke nasabah pada perubahan status
- [x] Notifikasi in-app ke petugas saat ditugaskan

### 8.4 Modul 2 / 3 / 10 — Identitas, lupa password, bukti ✅
- [x] `ForgotPasswordView` + `ResetPasswordView` + token berumur pendek
- [x] (Opsional) kerangka verifikasi HP/email — hanya jika disepakati klien
- [x] Upload foto KTP privat untuk penarikan besar
- [x] Validasi tipe/ukuran file; larang executable
- [x] Field-level encryption NIK / data KTP at-rest
- [x] Threshold penarikan besar + wajib lampiran KTP
- [x] Unduh KTP/PDF role-gated (`download_views`)
- [x] Generate PDF bukti setoran & penarikan (`pdf_receipt.py`)
- [x] Metadata metode transfer bank / e-wallet (**tanpa** payment gateway)

### 8.5 Modul 11 — Masa berlaku poin 1 tahun ✅
- [x] Management command `expire_poin` (1 tahun)
- [x] Audit log dan/atau notifikasi saat poin hangus
- [x] `PoinInfoView` — info sisa masa berlaku poin untuk nasabah

### 8.6 Modul 9 / 16 — Notifikasi & laporan (sebagian) ✅
- [x] Model `Notifikasi` + list / `read/` / `mark-all-read/`
- [x] Scope: nasabah & petugas hanya milik sendiri; staff filter `?user=`
- [x] FCM: register device token + kirim event jemput/penarikan/pengumuman/harga
- [x] Payload FCM tanpa NIK/KTP/token
- [x] Email transactional admin (penjemputan baru, ringkasan harian)
- [x] Kredensial FCM / WA / SMTP hanya di env
- [x] Export laporan Excel server-side (`openpyxl`)
- [x] Laporan evaluasi: field kendala + rekomendasi tindak lanjut
- [x] Kebijakan retensi/arsip digital transaksi minimal 5 tahun

### 8.9 Privacy policy endpoint ✅
- [x] `GET /api/privacy-policy/` — `PrivacyPolicyView` + service konten

---

## Fase 0: Foundation ✅

### 0.1 Project Setup ✅
- [x] Django project (`core/`), app `api`
- [x] `settings.py` (DB, CORS, JWT, DRF)
- [x] Dockerfile & docker-compose.yml; `.env.example`
- [x] Dependencies: DRF, simplejwt, django-filter, cors-headers, drf-spectacular, psycopg2

### 0.2 Database Models ✅
- [x] `User`, `KategoriSampah`, `TransaksiSetoran` + `DetailSetoran`
- [x] `Penjemputan`, `PenarikanSaldo`, `Reward` + `PenukaranPoin`
- [x] `MitraPengepul` + `PenjualanMitra`, `Pengaduan`
- [x] Initial migrations

### 0.3 Core API Setup ✅
- [x] Serializers, ViewSets, DefaultRouter
- [x] Permissions role-based; JWT login/refresh
- [x] drf-spectacular; `/health/`

---

## Fase 1: MVP — Infrastruktur & Auth ✅

### 1.1–1.2 Konfigurasi & Envelope ✅
- [x] Env-based secrets; WIT timezone
- [x] JSON envelope `success` / `status_code` / `message` / `data` / `meta`
- [x] Pagination, filters, exception handler, custom renderer

### 1.3–1.4 Auth & Pengguna (Modul 2 / 1) ✅
- [x] Login, refresh, me, registrasi nasabah
- [x] Filter users; nasabah tidak ubah role/saldo/poin via PATCH

### 1.5–1.6 Seed & Kategori (Modul 4–5) ✅
- [x] `seed_data`; CRUD kategori; `stok_terkini_kg`

---

## Fase 2: MVP — Logika Bisnis Inti ✅

- [x] Atomic ledger + `select_for_update`
- [x] Setoran (Modul 6/8/9), penjemputan (7), penarikan (10), tukar poin (11)
- [x] Penjualan mitra & stok (12–13), pengaduan (14)
- [x] Permission & queryset per role termasuk `pemerintah` read-only

---

## Fase 3: MVP — Operasional Harian ✅

- [x] Aksi approve/reject/assign setoran–jemput–tarik–tukar
- [x] `GET /api/activity/`; profil/QR; katalog reward

---

## Fase 4: MVP — Monitoring & Laporan ✅

- [x] Dashboard overview / chart / recent activity
- [x] Laporan daily / weekly / monthly / waste / evaluation
- [x] Inventory + history

---

## Fase 5: MVP Lengkap — Governance ✅

- [x] Audit log; pengaturan institusi; pengumuman
- [x] Riwayat harga; role pemerintah; consent UU PDP
- [x] Enkripsi NIK diselesaikan di Fase 8.4 ✅

---

## Fase 6: Kualitas & Dokumentasi ✅

- [x] Suite test (auth, deposits, pickups, withdrawals, permissions, dll.)
- [x] OpenAPI / Swagger `/api/docs/`
- [x] Error handling envelope + kode domain

---

## Definisi "Selesai" per Tahap

| Tahap | Kriteria |
|-------|----------|
| **MVP** | Fase 0–4 selesai; web admin operasional |
| **MVP Lengkap** | Fase 5 selesai; audit & pengaturan aktif |
| **UAT / Production Ready** | Fase 6–7 selesai; deploy staging + backup + monitoring |
| **Go-Live** | Production deploy + backup aktif + monitoring aktif + test restore lolos |
| **Pengembangan Lanjutan** | Fase 8 iteratif — sisa WA/Maps/import/infra sesuai prioritas |

## Indeks dokumen keamanan lintas repo

| Repo | Dokumen |
|------|---------|
| Backend (kanonik) | `.ai-steering/11-security-and-privacy.md` |
| Web Admin | `web-admin/.ai-steering/11-security-and-privacy.md` |
| Mobile | `mirumobileapp/.ai-steering/11-security-and-privacy.md` |
