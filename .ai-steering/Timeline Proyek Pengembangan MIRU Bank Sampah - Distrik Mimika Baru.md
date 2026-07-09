## **PT. Webekspres Teknologi Indonesia**

Jl. Raya Proklamasi, Gang Adhimix, Kompleks Perumahan Bumi Indah Proklamasi Blok F1 Nomor 12A

Tunggakjati, Karawang Barat, Kabupaten Karawang - Jawa Barat, 41311

## **DOKUMEN TIMELINE PROYEK**

## **PROYEK PENGEMBANGAN SISTEM MIRU BANK SAMPAH (MIRU-G)**
## **DISTRIK MIMIKA BARU, KABUPATEN MIMIKA, PAPUA TENGAH**
## **PLATFORM: BACKEND API (DJANGO) + WEB ADMIN (NEXT.JS) + MOBILE APP (FLUTTER)**

## **1. INFORMASI PROYEK**

| Item | Detail |
|------|--------|
| Nama Proyek | Aplikasi Inovasi Bank Sampah Distrik Mimika Baru **"MIRU BANK SAMPAH" (Miru-G)** |
| Klien | Pemerintah Distrik Mimika Baru (Kepala Distrik: Merlyn Temorubun, S,STP) |
| Durasi | **60 hari kerja** (Senin–Jumat, 08.00–17.00 WIT) |
| Tanggal Mulai | 07/07/2026 |
| Teknologi | Django REST API, PostgreSQL, Next.js, TypeScript, Tailwind CSS, Flutter |
| Repositori | `backend`, `web-admin`, `mirumobileapp` + infrastruktur deployment |
| Metodologi Pengembangan | Incremental Development & Requirement Locking |

## **2. KETENTUAN UMUM TIMELINE**

1. Timeline proyek disusun sebagai acuan pelaksanaan pekerjaan antara PIHAK PERTAMA dan PIHAK KEDUA.
2. Timeline bersifat estimasi dan dapat mengalami penyesuaian sesuai kondisi proyek.
3. Penyesuaian timeline dapat terjadi apabila:
   - a. Terjadi keterlambatan pemberian data, konten, atau approval dari PIHAK KEDUA
   - b. Terdapat perubahan kebutuhan sistem setelah tahap analisis
   - c. Terjadi revisi mayor atau Change Request (CR)
   - d. Terjadi kendala teknis di luar kendali PIHAK PERTAMA
4. Seluruh tahapan dalam timeline saling berkaitan dan bergantung pada proses validasi dari kedua pihak.
5. Timeline mulai berlaku sejak:
   - a. Perjanjian kerja sama disetujui
   - b. Pembayaran awal (DP) diterima
   - c. Tahap analisis proyek dimulai

## **3. RINGKASAN CAKUPAN MODUL (17 MODUL SISTEM)**

| No | Modul | Backend | Web Admin | Mobile |
|----|-------|---------|-----------|--------|
| 1 | Manajemen Akses & Pengguna | ✅ | ✅ | — |
| 2 | Autentikasi & Akun Nasabah | ✅ | ✅ | ✅ |
| 3 | Profil & Kartu Digital | ✅ | ✅ | ✅ |
| 4 | Informasi & Edukasi Sampah | ✅ | ✅ | ✅ |
| 5 | Katalog & Harga Sampah | ✅ | ✅ | ✅ |
| 6 | Setor Sampah Langsung | ✅ | ✅ | — |
| 7 | Penjemputan Sampah | ✅ | ✅ | ✅ |
| 8 | Penimbangan & Verifikasi | ✅ | ✅ | — |
| 9 | Saldo & Riwayat Transaksi | ✅ | ✅ | ✅ |
| 10 | Penarikan Saldo | ✅ | ✅ | ✅ |
| 11 | Poin & Reward | ✅ | ✅ | ✅ |
| 12 | Stok Gudang | ✅ | ✅ | — |
| 13 | Penjualan ke Mitra | ✅ | ✅ | — |
| 14 | Pengaduan Nasabah | ✅ | ✅ | ✅ |
| 15 | Dashboard & Monitoring | ✅ | ✅ | ✅ |
| 16 | Laporan & Ekspor Data | ✅ | ✅ | — |
| 17 | Pengaturan Sistem & Audit Log | ✅ | ✅ | — |

## **4. DETAIL TIMELINE PROYEK**


## **TAHAP 1 — ANALISIS, DISCOVERY & SYSTEM LOCKING**

| **Hari** | **Tanggal** | **Proyek** | **Aktivitas** | **Output** | **Progress (%)** |
|---|---|---|---|---|---|
| Hari 1 | 07/07/2026 | Semua | Persiapan proyek & penyusunan timeline kerja MIRU Bank Sampah | Timeline awal proyek | 2% |
| Hari 2 | 08/07/2026 | Semua | Kickoff proyek (Tim Developer + Koordinator Distrik Mimika Baru) | Dokumen kickoff | 4% |
| Hari 3 | 09/07/2026 | Semua | Analisis proses bisnis bank sampah (SOP setor langsung, penjemputan, penarikan, poin) | Draft business process | 5% |
| Hari 4 | 10/07/2026 | Mobile | Analisis aplikasi mobile nasabah (Flutter) — alur login, home, penjemputan, tarik saldo | Draft mobile workflow | 7% |
| Hari 5 | 13/07/2026 | Web Admin | Analisis dashboard web admin — alur petugas, admin, koordinator, pemerintah distrik | Draft admin workflow | 9% |
| Hari 6 | 14/07/2026 | Backend | Analisis role & hak akses sistem (nasabah, petugas, admin, koordinator, pemerintah, mitra) | Struktur user access | 10% |
| Hari 7 | 15/07/2026 | Semua | Analisis struktur 17 modul sistem & pemetaan fitur per platform | Draft struktur modul | 12% |
| Hari 8 | 16/07/2026 | Semua | Diskusi Grup / Meeting Online — validasi workflow operasional bank sampah lapangan | Draft workflow lapangan | 14% |
| Hari 9 | 17/07/2026 | Backend | Analisis business rules (min 1 kg setoran, min 5 kg jemput, min Rp50.000 tarik, perhitungan poin) | Draft business rules | 15% |
| Hari 10 | 20/07/2026 | Semua | Analisis kontrak API & integrasi antar platform (Backend ↔ Web Admin ↔ Mobile) | Draft API integration map | 17% |
| Hari 11 | 21/07/2026 | Semua | Diskusi Grup / Meeting Online — validasi kebutuhan fitur & prioritas MVP | Final kebutuhan sistem | 19% |
| Hari 12 | 22/07/2026 | Semua | Penyusunan Dokumen SRS, workflow final & Approval System Locking | SRS disetujui | 20% |

## **TAHAP 2 — DEVELOPMENT BACKEND API (Django + PostgreSQL)**

| **Hari** | **Tanggal** | **Proyek** | **Aktivitas** | **Output** | **Progress (%)** |
|---|---|---|---|---|---|
| Hari 13 | 23/07/2026 | Backend | Konfigurasi keamanan dasar (.env, SECRET_KEY, timezone Asia/Jayapura, ALLOWED_HOSTS) | Environment aman | 22% |
| Hari 14 | 24/07/2026 | Backend | Standar API response — JSON envelope, pagination, exception handler, renderer | Standar API response | 24% |
| Hari 15 | 27/07/2026 | Backend | Modul 2 — Autentikasi JWT (login, refresh, GET /api/auth/me/) | Login & token access | 25% |
| Hari 16 | 28/07/2026 | Backend | Modul 1 — Manajemen pengguna (CRUD, filter role, validasi field sensitif) | Modul user management | 27% |
| Hari 17 | 29/07/2026 | Backend | Seed data — 8 kategori sampah, 4 reward, user admin default (management command) | Data awal terisi | 29% |
| Hari 18 | 30/07/2026 | Backend | Modul 4–5 — Kategori & harga sampah (CRUD, stok_terkini_kg, endpoint public) | Modul katalog & harga | 30% |
| Hari 19 | 31/07/2026 | Backend | Integritas transaksional — transaction.atomic(), select_for_update(), validasi saldo/stok | Lapisan integritas data | 32% |
| Hari 20 | 03/08/2026 | Backend | Modul 6, 8, 9 — Transaksi setoran (validasi min 1 kg, auto-hitung harga, +saldo +poin +stok) | Modul setor sampah | 34% |
| Hari 21 | 04/08/2026 | Backend | Modul 7 — Penjemputan sampah (state machine status, validasi H+1 & min 5 kg) | Modul penjemputan | 35% |
| Hari 22 | 05/08/2026 | Backend | Modul 10 — Penarikan saldo (validasi min Rp50.000, cegah double approve) | Modul penarikan saldo | 37% |
| Hari 23 | 06/08/2026 | Backend | Modul 11 — Poin & reward (katalog CRUD, penukaran poin, kurangi stok reward) | Modul poin & reward | 39% |
| Hari 24 | 07/08/2026 | Backend | Modul 12–13 — Stok gudang & penjualan ke mitra pengepul | Modul gudang & mitra | 40% |
| Hari 25 | 10/08/2026 | Backend | Modul 14 — Pengaduan nasabah (jenis_pengaduan, tindak_lanjut, status workflow) | Modul pengaduan | 42% |
| Hari 26 | 11/08/2026 | Backend | Permission per role & queryset filtering (nasabah, petugas, admin, koordinator, pemerintah) | RBAC lengkap | 44% |
| Hari 27 | 12/08/2026 | Backend | Endpoint action penjemputan (approve, reject, assign petugas, update-status) | Workflow penjemputan API | 45% |
| Hari 28 | 13/08/2026 | Backend | Endpoint action penarikan & penukaran + GET /api/riwayat/ gabungan + profil/kartu digital | Alur operasional API | 47% |
| Hari 29 | 14/08/2026 | Backend | Modul 15 — Dashboard API (overview, grafik setoran, aktivitas terbaru) | Dashboard API | 49% |

**Catatan:** Tanggal 17/08/2026 tidak digunakan karena Hari Kemerdekaan RI.

| Hari 30 | 18/08/2026 | Backend | Modul 16–17 — Laporan API (harian/mingguan/bulanan), audit log & pengaturan institusi | Laporan & governance API | 50% |

## **TAHAP 3 — DEVELOPMENT WEB ADMIN (Next.js + TypeScript)**

| **Hari** | **Tanggal** | **Proyek** | **Aktivitas** | **Output** | **Progress (%)** |
|---|---|---|---|---|---|
| Hari 31 | 19/08/2026 | Web Admin | Setup infrastruktur — SWR, API client JWT, TypeScript types, folder structure | Fondasi web admin | 52% |
| Hari 32 | 20/08/2026 | Web Admin | Modul 2 — Login page, AuthProvider, role-based redirect, protected layout | Auth & session web | 53% |
| Hari 33 | 21/08/2026 | Web Admin | Layout dashboard — Sidebar, Header, navigasi 17 modul, logout, handle 401 | Navigation flow admin | 55% |
| Hari 34 | 24/08/2026 | Web Admin | Modul 15 — Dashboard overview (stat cards, grafik setoran Recharts, aktivitas terbaru) | Dashboard admin | 57% |
| Hari 35 | 25/08/2026 | Web Admin | Modul 1, 3 — Manajemen nasabah (list, search, detail profil, CRUD, riwayat transaksi) | Modul nasabah | 58% |
| Hari 36 | 26/08/2026 | Web Admin | Modul 4–5 — Kategori & harga sampah (CRUD kategori, edit harga_beli_per_kg) | Modul katalog & harga | 60% |
| Hari 37 | 27/08/2026 | Web Admin | Modul 6, 8 — Input setoran multi-kategori (auto-hitung subtotal) + riwayat transaksi | Modul setor langsung | 62% |
| Hari 38 | 28/08/2026 | Web Admin | Modul 7 — Penjemputan (tab status, approve/reject, assign petugas, update status) | Modul penjemputan | 63% |
| Hari 39 | 31/08/2026 | Web Admin | Modul 10–11 — Penarikan saldo & penukaran poin (list, approve/reject) | Modul saldo & poin | 65% |
| Hari 40 | 01/09/2026 | Web Admin | Modul 12–13 — Stok gudang, CRUD mitra pengepul, form penjualan ke mitra | Modul gudang & penjualan | 67% |
| Hari 41 | 02/09/2026 | Web Admin | Modul 14 — Pengaduan (list terbuka/ditutup, detail, form tindak lanjut) | Modul pengaduan | 68% |
| Hari 42 | 03/09/2026 | Web Admin | Modul 16 — Laporan (filter harian/mingguan/bulanan, tabel rekap, ekspor CSV/Excel) | Modul laporan | 70% |
| Hari 43 | 04/09/2026 | Web Admin | Modul 17 — Pengaturan institusi, pengumuman, audit log viewer + loading & toast UX | Pengaturan & polish UI | 72% |

## **TAHAP 4 — DEVELOPMENT MOBILE APP (Flutter)**

| **Hari** | **Tanggal** | **Proyek** | **Aktivitas** | **Output** | **Progress (%)** |
|---|---|---|---|---|---|
| Hari 44 | 07/09/2026 | Mobile | Setup Flutter — provider, dio, go_router, secure storage, theme MIRU, API client | Fondasi mobile app | 73% |
| Hari 45 | 08/09/2026 | Mobile | Modul 2 — AuthProvider, SplashScreen, LoginScreen, RegisterScreen, token persistence | Auth mobile | 75% |
| Hari 46 | 09/09/2026 | Mobile | Modul 15 — HomeScreen (saldo, poin, quick actions, info harga, aktivitas terbaru) | Dashboard nasabah | 77% |
| Hari 47 | 10/09/2026 | Mobile | Modul 3 — ProfileScreen & QRCodeScreen (kartu digital ID nasabah) | Profil & kartu digital | 78% |
| Hari 48 | 11/09/2026 | Mobile | Modul 4–5 — InfoSampahScreen (list kategori, harga per kg, panduan pemilahan) | Info & edukasi sampah | 80% |
| Hari 49 | 14/09/2026 | Mobile | Modul 7 — PenjemputanScreen & AjukanPenjemputanScreen (form multi-step, min 5 kg, H+1) | Modul penjemputan | 82% |
| Hari 50 | 15/09/2026 | Mobile | Modul 9–10 — RiwayatScreen (tab setoran/penarikan/poin) & TarikSaldoScreen | Riwayat & tarik saldo | 83% |

**Catatan:** Tanggal 16/09/2026 tidak digunakan karena Tahun Baru Islam 1448 H.

| Hari 51 | 17/09/2026 | Mobile | Modul 11 — RewardScreen & TukarPoinScreen (katalog reward, konfirmasi penukaran) | Modul poin & reward | 85% |
| Hari 52 | 18/09/2026 | Mobile | Modul 14 — PengaduanScreen & form pengaduan + bottom navigation & UX polish | Pengaduan & navigasi | 87% |

## **TAHAP 5 — INTEGRASI, QA & STABILISASI**

| **Hari** | **Tanggal** | **Proyek** | **Aktivitas** | **Output** | **Progress (%)** |
|---|---|---|---|---|---|
| Hari 53 | 21/09/2026 | Integrasi | Integrasi end-to-end Backend ↔ Web Admin (setoran, penjemputan, penarikan, laporan) | Integrasi web valid | 88% |
| Hari 54 | 22/09/2026 | Integrasi | Integrasi end-to-end Backend ↔ Mobile (login, penjemputan, tarik saldo, pengaduan) | Integrasi mobile valid | 90% |
| Hari 55 | 23/09/2026 | Semua | Internal QA testing — API, web admin, mobile (regresi alur SOP operasional) | QA report | 92% |
| Hari 56 | 24/09/2026 | Semua | Bugfixing & stabilisasi sistem (error handling, permission, edge cases) | Sistem distabilkan | 93% |

## **TAHAP 6 — USER ACCEPTANCE TESTING (UAT)**

| **Hari** | **Tanggal** | **Proyek** | **Aktivitas** | **Output** | **Progress (%)** |
|---|---|---|---|---|---|
| Hari 57 | 25/09/2026 | Web Admin | UAT web admin — admin, petugas, koordinator & pemerintah distrik | Feedback admin web | 95% |
| Hari 58 | 28/09/2026 | Mobile | UAT aplikasi mobile nasabah + validasi final workflow & business rules SOP | Feedback mobile app | 97% |

## **TAHAP 7 — REVISI MINOR**

| **Hari** | **Tanggal** | **Proyek** | **Aktivitas** | **Output** | **Progress (%)** |
|---|---|---|---|---|---|
| Hari 59 | 29/09/2026 | Semua | Pengerjaan revisi minor berdasarkan feedback UAT (UI, validasi, teks, alur kecil) | Minor revision | 98% |

## **TAHAP 8 — FINALISASI & DEPLOYMENT**

| **Hari** | **Tanggal** | **Proyek** | **Aktivitas** | **Output** | **Progress (%)** |
|---|---|---|---|---|---|
| Hari 60 | 30/09/2026 | Infrastruktur | Dokumentasi pengguna, deployment production (Gunicorn/Nginx/SSL), training & serah terima | Project completed | 100% |

## **5. KETENTUAN KHUSUS IMPLEMENTASI**

1. Prioritas pengembangan: **Backend API** → **Web Admin** → **Mobile App** → **Deployment**.
2. Web Admin digunakan oleh petugas, admin, koordinator, dan pemerintah distrik (read-only untuk pemerintah).
3. Mobile App (Flutter) ditujukan untuk nasabah/masyarakat — setor via petugas, penjemputan & tarik saldo via aplikasi.
4. Mitra/pengepul tidak memiliki akun login; dicatat sebagai data referensi oleh admin.
5. Sistem wajib HTTPS (SSL) pada environment production.
6. Fitur di luar cakupan MVP (payment gateway otomatis, GPS tracking, integrasi timbangan digital) memerlukan Change Request terpisah.

## **6. KETENTUAN PERUBAHAN TIMELINE**

1. Timeline dapat diperpanjang apabila PIHAK KEDUA terlambat memberikan feedback/approval, terdapat revisi mayor/CR, atau perubahan kebutuhan setelah system locking.
2. Penyesuaian timeline akan diinformasikan kepada PIHAK KEDUA secara profesional dan wajar.
3. Jika dalam waktu 3 (tiga) hari kerja tidak terdapat feedback dari PIHAK KEDUA pada tahap validasi tertentu, tahap tersebut dapat dianggap disetujui sementara (auto-approval) untuk menjaga kelangsungan timeline proyek.

_Catatan: untuk aktivitas yang mengikutsertakan PIHAK KEDUA (meeting validasi, UAT, training) diberi tanda dengan teks berwarna **biru** pada versi presentasi._

## **7. PENUTUP**

Dokumen Timeline Proyek ini merupakan bagian tidak terpisahkan dari Perjanjian Kerja Sama (MoU) dan menjadi acuan pelaksanaan proyek antara kedua belah pihak selama proses pengembangan berlangsung.

---

_Dokumen digenerate otomatis — 07/07/2026_