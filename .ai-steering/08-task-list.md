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
> **Kerja aktif #1:** sisa go-live **Fase 7** (test restore) + sisa **Fase 8** opsional (WA, Maps, bulk import, job queue).
> Audit Temuan backend (T0–T10) sudah ✅ — arsip BAGIAN B.
> Klien: Web Audit ✅; Mobile masih punya sisa temuan UI — lihat `mirumobileapp/.ai-steering/08-task-list.md`.
> **Tidak boleh** menambah fitur di luar 17 modul tanpa addendum.

### Cakupan 17 Modul Backend

| No | Modul | Status API | Sisa / catatan |
|----|-------|------------|----------------|
| 1 | Manajemen Akses & Pengguna | ✅ | Bulk import nasabah (belum) |
| 2 | Autentikasi & Akun Nasabah | ✅ | Lupa password ✅; verifikasi HP/email opsional ✅ |
| 3 | Profil & Kartu Digital | ✅ | NIK **tidak** disimpan (PDP); QR kartu digital ✅ |
| 4 | Informasi & Edukasi Sampah | ✅ | CRUD + list/detail edukasi ✅ |
| 5 | Katalog & Harga Sampah | ✅ | Kebijakan harga H-3 ✅ |
| 6 | Setor Sampah Langsung | ✅ | PDF bukti ✅ |
| 7 | Penjemputan Sampah | ✅ | Wilayah + kuota + lat/lng opsional ✅; Maps key (belum) |
| 8 | Penimbangan & Verifikasi | ✅ | — |
| 9 | Saldo & Riwayat Transaksi | ✅ | In-app + FCM ✅; WhatsApp (belum) |
| 10 | Penarikan Saldo | ✅ | PDF + lampiran KTP sementara (≥1jt, hapus setelah proses) ✅ |
| 11 | Poin & Reward | ✅ | Kedaluwarsa poin 1 tahun ✅ |
| 12 | Stok Gudang | ✅ | — |
| 13 | Penjualan ke Mitra | ✅ | — |
| 14 | Pengaduan Nasabah | ✅ | — |
| 15 | Dashboard & Monitoring | ✅ | Cache Redis (belum, opsional) |
| 16 | Laporan & Ekspor Data | ✅ | Excel server-side + evaluasi ✅ |
| 17 | Pengaturan Sistem & Audit Log | ✅ | Retensi 5 tahun ✅; privacy policy endpoint ✅ |

---

## Urutan kerja disarankan (lintas repo)

1. **Backend sisa go-live** — test restore backup; CORS/HTTPS + privacy URL.
2. Backend opsional — WA channel, Maps, bulk import, Celery/Redis.
3. Dukung sisa Audit Temuan **mobile** (kontrak API sudah ✅).
4. Web Admin Audit Temuan sudah selesai.
5. **Jangan** kerjakan Out of Scope tanpa addendum.

---

# BAGIAN A — BELUM SELESAI (prioritas atas)

> Hanya item `[ ]`. Detail cukup untuk dikerjakan tanpa menebak di luar 17 modul.

---

## Fase 7: Production Ready — sisa go-live
  *(Audit Temuan T0–T10 sudah ✅ di BAGIAN B.)*

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
  - Saat diaktifkan: jangan kirim token, password, foto KTP, atau isi lampiran ke Sentry
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
  - Payload **tanpa** foto KTP, saldo penuh, atau token JWT
  - Kredensial hanya di env (`WA_*` / setara) — jangan commit ke repo
  - Fallback: jika WA gagal, in-app/FCM tetap jalan; log error tanpa PII
  - Dokumentasikan opt-in / nomor HP sumber (dari profil nasabah)

### 8.7 Modul 7 — Integrasi peta sederhana

> **Sumber:** Jawaban §6.6.1; Constraints §5; Security §11 (API key di-restrict).
> **Bukan** GPS live tracking armada.
> Field lat/lng opsional di model/serializer penjemputan **sudah ✅** (T3 / BAGIAN B).

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
- [ ] **CDN untuk media files** — hanya jika traffic media/PDF naik nyata (bukan untuk lampiran KTP)
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


## Audit Temuan — selesai ✅

### T0. Envelope error & pesan BI (lintas modul)

- [x] **Audit pesan validasi / throttle / 4xx** agar selalu envelope BI, field-level jika ada
  - Rate limit login: ganti teks Inggris (`Expected available in …`) → mis. “Terlalu banyak percobaan. Coba lagi dalam X detik.”
  - Login gagal: bedakan (atau samakan secara aman) pesan username tidak ada vs password salah — **ikuti keputusan produk di temuan** (lihat T2); jangan biarkan mobile dapat generic “terjadi kesalahan”
  - Penarikan / setoran / jemput / tukar poin: pastikan `errors` per field ikut di response (bukan hanya `message` generik “satu atau lebih field tidak valid”)
  - Notifikasi setoran: pastikan payload nilai Rupiah **benar** (bug temuan: notif Rp0 padahal setoran ada nilai) — cek signal/serializer yang membentuk teks notif

### T1. Modul 6 — Setoran (bug lookup & notifikasi nilai)

- [x] **Perbaiki lookup nasabah saat input setoran** (“ID nasabah tidak ditemukan padahal sudah benar”)
  - Reproduksi: cari by id / username / QR payload yang dipakai web
  - Pastikan filter role=`nasabah`, `is_active`, dan format ID (int vs string) konsisten dengan yang di-QR mobile
  - Tambah test API: lookup berhasil untuk id valid + gagal jelas untuk id salah
- [x] **Notifikasi in-app setelah setoran** menampilkan **total nilai benar** (bukan Rp0)
  - Cek timing signal vs `total_nilai` sudah terhitung; jangan notif sebelum side-effect selesai
  - Payload tanpa NIK/JWT; angka format Rupiah WIT

### T2. Modul 2 — Autentikasi, reset password, registrasi, verifikasi HP

> Temuan meminta alur OTP WhatsApp. Channel WA masih item 8.6 — kerjakan kontrak API dulu; implement kirim WA bisa stub/log di staging sampai kredensial siap.

- [x] **Login: pesan gagal spesifik & konsisten** untuk web + mobile
  - Password salah → pesan BI jelas
  - Username tidak terdaftar → pesan BI jelas (**sesuai temuan**; dokumentasikan trade-off enumerasi akun)
- [x] **Forgot password: jangan “sukses palsu” untuk username tidak ada**
  - Temuan: saat ini token tetap “terkirim” meski username tidak ada → ubah agar response memberitahu username tidak terdaftar **atau** (jika keamanan mengharuskan) response generik + **jangan** generate token
  - Pastikan tidak ada token orphan di DB untuk username invalid
- [x] **Alur reset password baru (OTP WA)** — ganti / perluas flow token panjang
  1. Submit username
  2. Konfirmasi nomor HP yang cocok dengan profil (jangan izinkan reset tanpa cocok nomor)
  3. Kirim **OTP** ke WhatsApp (env `WA_*`); pesan: cek notifikasi WhatsApp
  4. Verifikasi OTP → izinkan set password baru (dua field: password + konfirmasi; validasi sama + policy min length; unik dari password lama jika feasible)
  5. Setelah sukses → client arahkan ke login
  - Endpoint + OpenAPI + test; rate-limit OTP; OTP expire singkat; jangan log OTP/PII
- [x] **Registrasi nasabah disingkat + verifikasi HP OTP**
  - Step 1: nama lengkap, username (unik), password
  - Step 2: nomor HP + OTP WA → baru aktif / login
  - Field lain (alamat, RT/RW, dll.) dilengkapi belakangan di profil
- [x] **Gate transaksi jika alamat belum lengkap**
  - Nasabah tanpa alamat (+ koordinat/patokan maps + wilayah dari API jika dipakai) **tidak boleh** ajukan jemput / tarik / tukar (atau sesuai keputusan: blok jemput saja)
  - Response 400 BI jelas: “Lengkapi alamat di profil sebelum …”
  - Alamat: teks + lat/lng opsional + referensi wilayah (dropdown dari API wilayah)
- [x] **Flag verifikasi nomor HP**
  - Jika admin create/update nasabah dengan nomor HP → status **belum terverifikasi**
  - Saat login mobile: indikasikan `phone_verified=false` agar client arahkan ke layar verifikasi OTP
  - Endpoint verifikasi OTP HP (bisa reuse infrastruktur OTP reset)

### T3. Modul 7 — Penjemputan (alur approve, notifikasi, queryset, koordinat)

- [x] **Alur setujui + assign atomik**
  - Jangan biarkan status “aktif/disetujui” tanpa petugas: satu aksi/transaksi setujui+assign, atau tolak setujui jika `petugas` null
  - Sesuaikan serializer/action + test agar tidak ada jemput aktif tanpa petugas
- [x] **Notifikasi in-app ke admin/koordinator** saat nasabah ajukan jemput baru
  - Judul/isi BI: ada penjemputan baru, segera tindak lanjuti; deep-link id jemput
- [x] **Notifikasi ke petugas + admin** saat status jemput **selesai**
- [x] **Filter list jemput untuk petugas (dan non-admin sesuai role)**
  - Petugas: **jangan** tampilkan `menunggu` / `ditolak`; hanya jemput yang ditugaskan ke petugas tersebut (status aktif/dijadwalkan/dll. sesuai SOP)
  - Admin/koordinator tetap lihat sesuai matriks role
- [x] **Field koordinat / patokan lokasi** pada penjemputan (dukung maps mobile)
  - lat/lng opsional + validasi rentang; dokumentasikan bukan live tracking
  - Auto-fill dari profil nasabah diizinkan di client; server terima override alamat/koordinat per pengajuan
- [x] **Validasi jadwal jemput di server** (selaras UI mobile)
  - Tolak tanggal/jam di masa lalu; minimal ~1 jam dari sekarang (atau aturan WIT yang disepakati)
  - Pesan BI jelas

### T4. Modul 11 — Penukaran poin (snapshot harga poin, status, notifikasi)

- [x] **Snapshot `poin_dibutuhkan` saat pengajuan** di `PenukaranPoin`
  - Simpan nilai poin saat create; approve memakai snapshot **atau** kebijakan eksplisit: tolak approve + status `ditolak` jika harga katalog naik & poin tidak cukup
  - Temuan: saat ini cek ulang harga terbaru tanpa snapshot → dokumentasikan & implement keputusan (disarankan: snapshot + tidak ubah biaya setelah diajukan)
- [x] **Status ditolak / dibatalkan** untuk penukaran yang tidak bisa diproses (bukan menggantung `menunggu` selamanya)
- [x] **Notifikasi in-app ke admin** saat ada pengajuan tukar poin baru
- [x] **(Opsional lanjut) Quantity / multi-line redemption** — accepted scope: default qty=1 per baris sampai kontrak API multi-qty jelas (tidak diimplementasikan)

### T5. Modul 10 — Penarikan saldo (error field-level)

- [x] **Perbaiki validasi penarikan** agar error envelope menyebut field yang salah (nominal min, saldo kurang, metode, dll.)
  - Reproduksi bug temuan: submit gagal “satu atau lebih field tidak valid” tanpa detail → pastikan serializer errors ikut ke klien
  - Setelah sukses create: message BI inkl. SLA 1–2 hari kerja (client juga menampilkan notif sukses)

### T6. Modul 9 — Riwayat / activity detail

- [x] **Pastikan payload activity / detail setoran lengkap untuk mobile**
  - Per item setoran: jenis sampah, berat kg, petugas (jika ada), tanggal jemput/proses, jam
  - Endpoint detail yang dipakai RiwayatScreen mengembalikan nested details; test regresi

### T7. Modul 14 — Pengaduan

- [x] **Tambah pilihan jenis pengaduan `lainnya`** (atau setara) di choices model + migrasi + OpenAPI
  - Mobile form ikut opsi baru
- [x] **Notifikasi in-app ke admin** saat pengaduan baru masuk
- [x] **Validasi tutup pengaduan:** `tindak_lanjut` wajib sebelum status ditutup (400 BI jika kosong)

### T8. Modul 4 / 5 / 17 — Edukasi markdown, harga H-3, jam operasional

- [x] **Edukasi:** pastikan field `isi` mendukung Markdown (simpan teks mentah; render di client)
  - Tidak perlu HTML sanitizer berat di server; dokumentasikan subset Markdown yang diizinkan
- [x] **Harga H-3:** verifikasi API tetap enforce `tanggal_berlaku` ≥ H+3 + pengumuman (sudah ✅ — regresi test jika web form baru kirim field)
- [x] **Jam operasional institusi sebagai struktur waktu** (bukan free-text saja)
  - Model/serializer: mis. `jam_buka`, `jam_tutup` (TimeField) + hari; response ramah untuk mobile
  - Deprecate / stop mengandalkan teks bebas untuk jam
  - **Hapus / nonaktifkan field upload logo institusi** (logo fiks pakai ikon app) — jangan break client lama: field opsional diabaikan atau dihapus bertahap
- [x] **Peringatan jemput di luar jam layanan** — server boleh warning di response atau client-only; jika server: flag/meta di create jemput

### T9. Modul 15 — Dashboard petugas

- [x] **Overview / widget yang relevan untuk role `petugas`**
  - Minimal: jemput ditugaskan hari ini, antrian aktif milik sendiri (bukan angka admin penuh jika tidak diizinkan)
  - Pastikan permission overview tidak 403 untuk petugas **atau** endpoint ringkas khusus petugas

### T10. Modul 1 / 3 — Verifikasi HP setelah create admin

- [x] Lihat T2 flag `phone_verified`; pastikan create/update user dari admin meng-set unverified saat nomor diisi/diubah

---


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
- [x] **NIK tidak dikumpulkan / tidak disimpan** (selaras proposal: bukan field modul; PDP minimisasi)
- [x] Lampiran foto KTP **sementara** hanya penarikan ≥ Rp1.000.000 — bukan arsip profil
- [x] Validasi tipe/ukuran file; larang executable; nginx deny `/media/lampiran_ktp/`
- [x] Hapus file lampiran setelah approve/tolak (`purge_lampiran_ktp`); flag `ktp_diverifikasi`
- [x] Unduh lampiran role-gated hanya status `menunggu` + audit `view`
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
- [x] NIK tidak disimpan; lampiran KTP penarikan besar dihapus setelah proses (PDP) ✅

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
