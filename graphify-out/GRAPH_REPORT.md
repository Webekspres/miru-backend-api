# Graph Report - miru-backend  (2026-07-09)

## Corpus Check
- 112 files · ~60,651 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1536 nodes · 2858 edges · 155 communities (73 shown, 82 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 510 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b57518d1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Services
- Services 1
- Backend
- Backend 3
- Tests
- Docs
- Tests 6
- Backend 7
- Tests 8
- Backend 9
- Backend 10
- Tests 11
- Tests 12
- Tests 13
- Backend 14
- Services 15
- Backend 16
- Backend 17
- Backend 18
- Tests 19
- Services 20
- Backend 21
- Services 22
- Tests 23
- Tests 24
- Backend 25
- Tests 26
- Tests 27
- Services 28
- Backend 29
- Backend 30
- Backend 31
- Backend 32
- Backend 33
- Tests 34
- Tests 35
- Tests 36
- Tests 37
- Tests 38
- Tests 39
- Backend 40
- Backend 41
- Services 42
- Tests 43
- Tests 44
- Tests 45
- Tests 46
- Tests 47
- Services 48
- Backend 49
- Backend 50
- Tests 51
- Tests 52
- Tests 53
- Tests 54
- Tests 55
- Tests 56
- Backend 57
- Services 58
- Tests 59
- Misc
- Docs 61
- Backend 62
- Backend 63
- Tests 64
- Docs 65
- Backend 66
- Misc 67
- Docs 68
- Docs 69
- Docs 70
- Docs 71
- Docs 72
- Backend 73
- Backend 74
- Backend 75
- Backend 76
- Backend 77
- Backend 78
- Backend 79
- Backend 80
- Backend 81
- Misc 82
- Misc 83
- Docs 84
- Docs 85
- PenukaranPoinViewSet
- MIRU Bank Sampah (Miru-G) — Ekosistem Aplikasi
- Fase 2: MVP — Logika Bisnis Inti
- Urutan Pengerjaan Rekomendasi (Sprint)
- Jawaban_Persyaratan_MIRU_Bank_Sampah.md
- 02 — Architecture & Tech Stack (Backend)
- Fase 3: MVP — Operasional Harian (End-to-End)
- InstitutionSettingsTests
- PriceHistoryTests
- Fase 1: MVP — Infrastruktur & Auth
- 08 — Task List: Backend Development Roadmap
- Fase 5: MVP Lengkap — Governance
- Fase 7: Production Ready
- MeEndpointTests
- AdminCreateStaffTests
- RTK - Rust Token Killer
- MIRU Backend API — Agent Rules
- graphify
- Fase 0: Foundation ✅ Selesai
- Fase 4: MVP — Monitoring & Laporan
- Fase 6: Kualitas & Dokumentasi
- Fase 8: Post-MVP & Peningkatan
- get_privacy_policy
- 0010_alter_kategorisampah_options_and_more.py
- MIRU Bank Sampah (Miru-G)
- Role: Admin Aplikasi
- Role: Mitra/Pengepul
- Role: Nasabah
- Role: Pemerintah Distrik
- Role: Petugas Bank Sampah
- DetailSetoran Model
- KategoriSampah Model
- MitraPengepul Model
- Nasabah Poin Ledger (User.poin)
- Nasabah Saldo Ledger (User.saldo)
- PenarikanSaldo Model
- Penjemputan Model
- PenjualanMitra Model
- Reward Model
- TransaksiSetoran Model
- User Model
- API /api/auth/login/
- API /api/deposits/
- API /api/pickups/
- API /api/withdrawals/
- Deposit Side Effects (saldo+poin+stok atomik)
- Minimal Setoran 1 kg per Jenis
- Minimal Estimasi Penjemputan 5 kg
- Minimal Penarikan Saldo Rp50.000
- Pickup Status Workflow
- Konversi Poin: 1 poin per Rp1.000 setoran
- Constraint: No GPS Live Tracking
- Constraint: No Payment Gateway Integration
- AuditLog Model
- Waste Category Seed Data (8 kategori)
- EnvelopeAPITestCase Test Pattern
- GET/POST /api/deposits/
- GET/POST /api/pickups/
- seed_data Management Command

## God Nodes (most connected - your core abstractions)
1. `EnvelopeAPITestCase` - 80 edges
2. `KategoriSampah` - 65 edges
3. `success_response()` - 56 edges
4. `TransaksiSetoran` - 46 edges
5. `User` - 45 edges
6. `AlreadyProcessedError` - 44 edges
7. `PenarikanSaldo` - 38 edges
8. `Reward` - 37 edges
9. `Command` - 33 edges
10. `IsMonitorReadOnly` - 30 edges

## Surprising Connections (you probably didn't know these)
- `Meta` --uses--> `TransaksiSetoran`  [INFERRED]
  api/filters.py → api/models.py
- `Docker Compose Django Web Service` --implements--> `Django REST API Backend`  [INFERRED]
  docker-compose.yml → .ai-steering/02-architecture-and-stack.md
- `DetailSetoranReadSerializer` --uses--> `AlreadyProcessedError`  [INFERRED]
  api/serializers.py → api/exceptions.py
- `DetailSetoranSerializer` --uses--> `AlreadyProcessedError`  [INFERRED]
  api/serializers.py → api/exceptions.py
- `KategoriSampahSerializer` --uses--> `AlreadyProcessedError`  [INFERRED]
  api/serializers.py → api/exceptions.py

## Import Cycles
- None detected.

## Communities (155 total, 82 thin omitted)

### Community 0 - "Services"
Cohesion: 0.07
Nodes (47): AbstractUser, DetailSetoran, User, PenjualanMitraCreateSerializer, adjust_setoran_correction(), complete_penukaran_poin(), create_setoran_with_side_effects(), credit_nasabah_setoran() (+39 more)

### Community 1 - "Services 1"
Cohesion: 0.08
Nodes (56): DashboardDepositChartView, DashboardOverviewView, DashboardRecentActivityView, InventoryHistoryView, InventoryView, MonitorView, Monitoring endpoints: dashboard (Modul 15), laporan (Modul 16), inventory (Modul, Base view for admin/koordinator/pemerintah read-only monitoring. (+48 more)

### Community 2 - "Backend"
Cohesion: 0.07
Nodes (32): MeView, MiruTokenObtainPairSerializer, MiruTokenObtainPairView, MiruTokenRefreshView, user_auth_payload(), _envelope(), get_demo_user(), get_nav_groups() (+24 more)

### Community 4 - "Tests"
Cohesion: 0.13
Nodes (13): PenarikanSaldo, Pengaduan, Penjemputan, PenukaranPoin, Reward, TransaksiSetoran, DashboardDepositChartTests, DashboardOverviewTests (+5 more)

### Community 6 - "Tests 6"
Cohesion: 0.11
Nodes (6): DailyReportTests, EvaluationReportTests, MonthlyReportTests, ReportTestMixin, WasteReportTests, WeeklyReportTests

### Community 7 - "Backend 7"
Cohesion: 0.08
Nodes (32): CurrentRequestMiddleware, get_client_ip(), get_current_request(), get_current_user(), Get the current user from thread-local storage., Extract client IP from request headers., Store the current request in thread-local storage., Access the current request from thread-local storage (for signals etc.). (+24 more)

### Community 8 - "Tests 8"
Cohesion: 0.06
Nodes (9): EnvelopeAPITestCase, Base test case with envelope helpers and user factories., LoginTests, PrivacyPolicyTests, RefreshTokenTests, UserPatchPermissionTests, UserResponseSecurityTests, WasteCategoryPublicReadTests (+1 more)

### Community 9 - "Backend 9"
Cohesion: 0.13
Nodes (16): AlreadyProcessedError, AuditLogSerializer, DetailSetoranReadSerializer, DetailSetoranSerializer, DetailSetoranWriteSerializer, Meta, MitraPengepulSerializer, NasabahLookupSerializer (+8 more)

### Community 10 - "Backend 10"
Cohesion: 0.18
Nodes (6): IsAdmin, PenarikanSaldoSerializer, success_response(), KategoriSampahViewSet, PenarikanSaldoViewSet, RewardViewSet

### Community 13 - "Tests 13"
Cohesion: 0.09
Nodes (5): AuditLog, AuditLogListTests, AuditLogSignalTests, DepositCorrectionTests, Verify automatic audit log recording via Django signals.

### Community 14 - "Backend 14"
Cohesion: 0.21
Nodes (9): PengaturanInstitusiSerializer, PengumumanSerializer, get_institution_settings(), Institution settings singleton helpers., Return the singleton institution settings row (creates defaults if missing)., InstitutionSettingsView, PengumumanListView, PrivacyPolicyView (+1 more)

### Community 15 - "Services 15"
Cohesion: 0.16
Nodes (11): InvalidStatusTransitionError, approve_pickup(), assign_pickup(), Decimal, Pickup request validation and status state machine., reject_pickup(), update_pickup_status(), validate_estimasi_berat() (+3 more)

### Community 17 - "Backend 17"
Cohesion: 0.16
Nodes (11): Meta, TransaksiSetoranFilter, IsUserOwnerOrAdmin, Object-level permission for the User model (/api/users/{id}/)., get_price_history(), Return price history queryset for a category., MiruPagination, ActivityListView (+3 more)

### Community 18 - "Backend 18"
Cohesion: 0.10
Nodes (3): PenjualanMitraSerializer, UserAdminSerializer, UserRegistrationSerializer

### Community 20 - "Services 20"
Cohesion: 0.16
Nodes (9): TransaksiSetoranCreateSerializer, build_bukti_digital(), build_detail_data(), prepare_details_data(), Decimal, Business rules and price calculation for deposit transactions., Struktur bukti digital untuk nasabah (SOP B.1)., validate_nasabah_for_setoran() (+1 more)

### Community 21 - "Backend 21"
Cohesion: 0.15
Nodes (13): filter_nasabah_owned(), filter_pickup_queryset(), filter_staff_only(), Reusable queryset filters per role., Admin/koordinator/pemerintah read; others denied., Nasabah sees own data; staff roles see all., get_activity_items(), _penarikan_items() (+5 more)

### Community 22 - "Services 22"
Cohesion: 0.24
Nodes (11): approve_withdrawal(), _ensure_pending(), Decimal, Business rules for saldo withdrawal requests., Tolak pengajuan — saldo tidak pernah didebit saat create, jadi tidak perlu refun, reject_withdrawal(), validate_approve_withdrawal(), validate_create_withdrawal() (+3 more)

### Community 24 - "Tests 24"
Cohesion: 0.03
Nodes (75): 10.1 Tujuan, 10.2 Alur Input Data, 10.3 Ketentuan, 10. SOP Input Data ke Aplikasi, 11.1 Tujuan, 11.2 Alur Penarikan Saldo, 11.3 Ketentuan, 11. SOP Penarikan Saldo Nasabah (+67 more)

### Community 25 - "Backend 25"
Cohesion: 0.16
Nodes (7): IsActivityReader, IsAdminOrKoordinator, IsPemerintahReadOnly, Pemerintah distrik: hanya boleh akses read (GET/HEAD/OPTIONS)., Nasabah (milik sendiri) atau staff read-all untuk riwayat gabungan., MitraPengepulViewSet, PenjualanMitraViewSet

### Community 28 - "Services 28"
Cohesion: 0.04
Nodes (48): 04 — API Contracts & Standards, 10. Mapping Role → Endpoint Access, 11. Catatan Implementasi, 1.1 Route Naming (English, kebab-case), 1. Prinsip Desain API, 2.1 Login, 2.2 Refresh Token, 2.3 Profil User Login (+40 more)

### Community 29 - "Backend 29"
Cohesion: 0.27
Nodes (3): IsPetugasOrAdmin, TransaksiSetoranReadSerializer, TransaksiSetoranViewSet

### Community 30 - "Backend 30"
Cohesion: 0.05
Nodes (39): **10.1 Mekanisme Revisi dan UAT**, **10. PRODUK DAN LAYANAN YANG DIDAPATKAN**, **11. PENUTUP**, **1.1 Pendahuluan**, **1.2 Tujuan**, **1.3 Cakupan Program dan Sistem**, **1. EXECUTIVE SUMMARY**, **2. PROFIL PERUSAHAAN** (+31 more)

### Community 31 - "Backend 31"
Cohesion: 0.22
Nodes (3): KategoriSampahSerializer, Admin-only: koreksi data transaksi setoran., TransaksiSetoranCorrectionSerializer

### Community 32 - "Backend 32"
Cohesion: 0.08
Nodes (24): 05 — Business Rules & SOPs, A.1 Konversi Setoran ke Saldo, A.2 Konversi Saldo ke Poin Reward, A.3 Penarikan Saldo, A.4 Penukaran Poin, A. Aturan Keuangan, B.1 Setor Langsung (di Kantor), B.2 Penjemputan (via Aplikasi) (+16 more)

### Community 33 - "Backend 33"
Cohesion: 0.15
Nodes (6): PengaduanCreateSerializer, PengaduanSerializer, PengaduanUpdateSerializer, Business rules for nasabah complaints., validate_admin_close(), validate_jenis_pengaduan()

### Community 37 - "Tests 37"
Cohesion: 0.09
Nodes (4): SOP A.4 — action endpoint approve., RedemptionActionTests, RedemptionApproveTests, RedemptionCreateTests

### Community 40 - "Backend 40"
Cohesion: 0.23
Nodes (3): IsStaffManagerOrPetugas, Admin, koordinator, atau petugas — untuk lookup nasabah., UserViewSet

### Community 41 - "Backend 41"
Cohesion: 0.13
Nodes (5): PenarikanSaldoCreateSerializer, PenjemputanCreateSerializer, PenjemputanUpdateSerializer, validate_jadwal_h_plus_one(), validate_nasabah_owner()

### Community 42 - "Services 42"
Cohesion: 0.21
Nodes (9): PenukaranPoinCreateSerializer, PenukaranPoinUpdateSerializer, approve_redemption(), _ensure_pending(), Business rules for reward point redemptions., validate_approve_redemption(), validate_create_redemption(), validate_poin_cukup() (+1 more)

### Community 44 - "Tests 44"
Cohesion: 0.11
Nodes (8): KategoriSampah, Meta, MitraPengepul, PenjualanMitra, InventoryHistoryTests, InventoryTests, MitraPengepulCrudTests, SeedDataFullTests

### Community 48 - "Services 48"
Cohesion: 0.08
Nodes (23): 09 — Data Dictionary & Reference Values (Backend), A.1 Daftar Jenis Sampah yang Diterima, A.2 Ketentuan Kategori, A. KATEGORI & HARGA SAMPAH (Seed Data), B. KATALOG REWARD (Seed Data), C.1 Konversi Setoran, C.2 Contoh Perhitungan (dari SOP), C.3 Aturan Keuangan Ringkas (+15 more)

### Community 49 - "Backend 49"
Cohesion: 0.10
Nodes (20): **1. INFORMASI PROYEK**, **2. KETENTUAN UMUM TIMELINE**, **3. RINGKASAN CAKUPAN MODUL (17 MODUL SISTEM)**, **4. DETAIL TIMELINE PROYEK**, **5. KETENTUAN KHUSUS IMPLEMENTASI**, **6. KETENTUAN PERUBAHAN TIMELINE**, **7. PENUTUP**, **DISTRIK MIMIKA BARU, KABUPATEN MIMIKA, PAPUA TENGAH** (+12 more)

### Community 50 - "Backend 50"
Cohesion: 0.36
Nodes (3): IsPickupManager, PenjemputanSerializer, PenjemputanViewSet

### Community 51 - "Tests 51"
Cohesion: 0.11
Nodes (4): DepositFlowTests, DepositReadFilterTests, SOP B.1 — petugas scan/cari nasabah → input setoran → bukti digital., datetime

### Community 52 - "Tests 52"
Cohesion: 0.10
Nodes (19): 07 — Modules & Features (Backend), 17 Modul Sistem — Peran Backend, Detail Endpoint Backend per Modul, Modul 10: Penarikan Saldo, Modul 11: Poin & Reward, Modul 12: Stok Gudang, Modul 13: Penjualan ke Mitra, Modul 14: Pengaduan (+11 more)

### Community 53 - "Tests 53"
Cohesion: 0.11
Nodes (17): 1. Environment Variables, 1. Setup Environment, 2. Build and Run, 2. Run Migrations & Server, 3. Run Migrations in Docker, 4. Seed Demo Data, 5. Run Tests, 6. Mobile — HP Fisik (Windows + Docker Desktop) (+9 more)

### Community 55 - "Tests 55"
Cohesion: 0.12
Nodes (15): 03 — Database Schema & ERD (Backend Django), 10. PenjualanMitra, 11. Pengaduan, 1. User (extends AbstractUser), 2. KategoriSampah, 3. TransaksiSetoran, 4. DetailSetoran, 5. Penjemputan (+7 more)

### Community 56 - "Tests 56"
Cohesion: 0.12
Nodes (15): **1. INFORMASI PROYEK**, **2. KETENTUAN UMUM TIMELINE**, **3. DETAIL TIMELINE PROYEK**, **4. KETENTUAN KHUSUS IMPLEMENTASI**, **5. KETENTUAN PERUBAHAN TIMELINE**, **6. PENUTUP**, Catatan:, Catatan: (+7 more)

### Community 57 - "Backend 57"
Cohesion: 0.13
Nodes (14): 06 — System Constraints (Batasan Sistem), 10. Publikasi Aplikasi, 11. Batasan Role, 12. Batasan Teknis Backend, 1. TIDAK ADA Integrasi Payment Gateway Otomatis, 2. TIDAK ADA GPS Live Tracking, 3. TIDAK ADA Integrasi Hardware Fisik, 4. TIDAK ADA Integrasi Dukcapil (+6 more)

### Community 58 - "Services 58"
Cohesion: 0.22
Nodes (7): PengaturanInstitusiAdmin, PengumumanAdmin, RiwayatHargaAdmin, PengaturanInstitusi, Pengumuman, Singleton — profil institusi bank sampah (pk selalu 1)., RiwayatHarga

### Community 59 - "Tests 59"
Cohesion: 0.14
Nodes (13): 00 — System Prompt & Clean Code Rules, 10. Documentation, 1. Struktur & Organisasi, 2. Models (Django ORM), 3. Serializers, 4. Views & ViewSets, 5. Permissions, 6. Error Handling (+5 more)

### Community 60 - "Misc"
Cohesion: 0.90
Nodes (4): handle(), main(), pipe(), socket

### Community 63 - "Backend 63"
Cohesion: 0.14
Nodes (13): 1. Extend `EnvelopeAPITestCase`, 2. Assert JSON Envelope (required), 3. File Organization, 4. What to Test per Feature, 5. Use English Routes, 6. Seed Data for Manual / Integration Tests, Do Not, MIRU Backend Feature Testing (+5 more)

### Community 64 - "Tests 64"
Cohesion: 0.15
Nodes (12): 01 — Project Overview: MIRU Bank Sampah (Miru-G), 3 Repositori Sistem, 6 Role Pengguna, Indikator Keberhasilan Program, Informasi Aplikasi, Informasi Kontak & Organisasi, Jam Layanan Operasional, Latar Belakang (+4 more)

### Community 66 - "Backend 66"
Cohesion: 0.17
Nodes (11): **6.1 Persyaratan Administratif Program**, **6.2 Persyaratan Data Operasional**, **6.3 Persyaratan Legalitas dan Kebijakan Internal**, **6.4 Persyaratan Akun Developer dan Publikasi Aplikasi**, **6.5 Persyaratan Infrastruktur dan Domain**, **6.6 Persyaratan Integrasi Pihak Ketiga**, **6.7 Persyaratan Perangkat Pendukung Operasional**, **6. PERSYARATAN DAN PERIZINAN YANG DISEDIAKAN KLIEN** (+3 more)

### Community 95 - "PenukaranPoinViewSet"
Cohesion: 0.26
Nodes (4): IsNasabah, IsOwnerOrAdmin, PenukaranPoinSerializer, PenukaranPoinViewSet

### Community 96 - "MIRU Bank Sampah (Miru-G) — Ekosistem Aplikasi"
Cohesion: 0.20
Nodes (9): 6 Role Pengguna, Arsitektur Sistem, Kontak & Instansi, MIRU Bank Sampah (Miru-G) — Ekosistem Aplikasi, Quick Start (Development Lokal), Referensi API Live (saat backend berjalan), Repositori GitHub, Standarisasi Lintas Repositori (+1 more)

### Community 97 - "Fase 2: MVP — Logika Bisnis Inti"
Cohesion: 0.22
Nodes (9): 2.1 Integritas Data Transaksional, 2.2 Transaksi Setoran (Modul 6, 8, 9), 2.3 Penjemputan Workflow (Modul 7), 2.4 Penarikan Saldo (Modul 10), 2.5 Penukaran Poin (Modul 11), 2.6 Penjualan Mitra & Stok (Modul 12–13), 2.7 Pengaduan (Modul 14), 2.8 Permission & Queryset per Role (+1 more)

### Community 98 - "Urutan Pengerjaan Rekomendasi (Sprint)"
Cohesion: 0.22
Nodes (9): Post-Launch — Fase 8, Sprint 1 (Minggu 1) — Fase 1, Sprint 2 (Minggu 2) — Fase 2.1–2.2, Sprint 3 (Minggu 3) — Fase 2.3–2.5, Sprint 4 (Minggu 4) — Fase 2.6–3, Sprint 5 (Minggu 5) — Fase 4, Sprint 6 (Minggu 6) — Fase 5–6, Sprint 7 (Minggu 7) — Fase 7 (+1 more)

### Community 99 - "Jawaban_Persyaratan_MIRU_Bank_Sampah.md"
Cohesion: 0.22
Nodes (8): **6.1 Persyaratan Administratif Program**, **6.2 Persyaratan Data Operasional**, **6.3 Persyaratan Legalitas dan Kebijakan Internal**, **6.4 Persyaratan Akun Developer dan Publikasi Aplikasi**, **6.5 Persyaratan Infrastruktur dan Domain**, **6.6 Persyaratan Integrasi Pihak Ketiga**, **6.7 Persyaratan Perangkat Pendukung Operasional**, **JAWABAN PERSYARATAN KLIEN**

### Community 100 - "02 — Architecture & Tech Stack (Backend)"
Cohesion: 0.25
Nodes (7): 02 — Architecture & Tech Stack (Backend), API Documentation, Arsitektur, CORS Configuration, Environment Variables (`.env`), Struktur Folder, Tech Stack

### Community 101 - "Fase 3: MVP — Operasional Harian (End-to-End)"
Cohesion: 0.25
Nodes (8): 3.1 Alur Setor Langsung (SOP B.1), 3.2 Alur Penjemputan (SOP B.2), 3.3 Alur Penarikan (SOP A.3), 3.4 Alur Penukaran Poin (SOP A.4), 3.5 Riwayat Transaksi Gabungan (Modul 9), 3.6 Profil & Kartu Digital (Modul 3), 3.7 Reward Katalog (Modul 11), Fase 3: MVP — Operasional Harian (End-to-End)

### Community 104 - "Fase 1: MVP — Infrastruktur & Auth"
Cohesion: 0.29
Nodes (7): 1.1 Konfigurasi & Keamanan Dasar ✅, 1.2 Standar API Response — JSON Envelope ✅, 1.3 Autentikasi & Registrasi (Modul 2) ✅, 1.4 Manajemen Pengguna (Modul 1) ✅, 1.5 Seed Data (Modul 4–5) ✅, 1.6 Kategori Sampah (Modul 4–5) ✅, Fase 1: MVP — Infrastruktur & Auth

### Community 105 - "08 — Task List: Backend Development Roadmap"
Cohesion: 0.33
Nodes (5): 08 — Task List: Backend Development Roadmap, Cakupan 17 Modul Backend, Definisi "Selesai" per Tahap, Gap Kode vs Dokumen (perlu ditangani), Ringkasan Fase

### Community 106 - "Fase 5: MVP Lengkap — Governance"
Cohesion: 0.33
Nodes (6): 5.1 Audit Log (Modul 17), 5.2 Pengaturan Institusi (Modul 17), 5.3 Riwayat Harga (Modul 5 — opsional MVP), 5.4 Role Pemerintah Distrik, 5.5 Kebijakan Data Pribadi (UU PDP), Fase 5: MVP Lengkap — Governance

### Community 107 - "Fase 7: Production Ready"
Cohesion: 0.33
Nodes (6): 7.1 Keamanan, 7.2 Deployment, 7.3 Backup & Recovery, 7.4 Monitoring & Logging, 7.5 Performance, Fase 7: Production Ready

### Community 110 - "RTK - Rust Token Killer"
Cohesion: 0.33
Nodes (5): graphify, Hook-Based Usage, Installation Verification, Meta Commands (always use rtk directly), RTK - Rust Token Killer

### Community 111 - "MIRU Backend API — Agent Rules"
Cohesion: 0.40
Nodes (4): Graphify Knowledge Graph, MIRU Backend API — Agent Rules, Stack, Token Savers (WAJIB)

### Community 112 - "graphify"
Cohesion: 0.40
Nodes (4): ⚠️ AI Steering — baca on-demand (jangan semua sekaligus), Aturan Keras, graphify, MIRU Bank Sampah — Backend API (Django)

### Community 113 - "Fase 0: Foundation ✅ Selesai"
Cohesion: 0.50
Nodes (4): 0.1 Project Setup ✅, 0.2 Database Models ✅, 0.3 Core API Setup ✅, Fase 0: Foundation ✅ Selesai

### Community 114 - "Fase 4: MVP — Monitoring & Laporan"
Cohesion: 0.50
Nodes (4): 4.1 Dashboard API (Modul 15), 4.2 Laporan API (Modul 16), 4.3 Stok Gudang (Modul 12), Fase 4: MVP — Monitoring & Laporan

### Community 115 - "Fase 6: Kualitas & Dokumentasi"
Cohesion: 0.50
Nodes (4): 6.1 Unit & Integration Tests, 6.2 API Documentation (OpenAPI), 6.3 Error Handling, Fase 6: Kualitas & Dokumentasi

### Community 116 - "Fase 8: Post-MVP & Peningkatan"
Cohesion: 0.50
Nodes (4): 8.1 Fitur Tambahan, 8.2 Optimasi & Skalabilitas, 8.3 Yang TIDAK BOLEH Diimplementasikan (System Constraints), Fase 8: Post-MVP & Peningkatan

## Knowledge Gaps
- **467 isolated node(s):** `Migration`, `Migration`, `Migration`, `Migration`, `Migration` (+462 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **82 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EnvelopeAPITestCase` connect `Tests 8` to `Tests`, `Tests 6`, `Tests 11`, `Tests 12`, `Tests 13`, `Tests 19`, `Tests 23`, `Tests 26`, `Tests 27`, `Tests 34`, `Tests 35`, `Tests 36`, `Tests 37`, `Tests 38`, `Tests 39`, `Tests 43`, `Tests 44`, `Tests 45`, `Tests 46`, `Tests 47`, `Tests 51`, `Tests 54`, `InstitutionSettingsTests`, `PriceHistoryTests`, `MeEndpointTests`, `AdminCreateStaffTests`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `KategoriSampah` connect `Tests 44` to `Services`, `Services 1`, `Tests 34`, `Backend 3`, `Tests`, `Tests 35`, `Tests 6`, `Backend 7`, `Tests 8`, `PriceHistoryTests`, `Tests 13`, `Tests 51`, `Services 20`, `Tests 19`, `Tests 23`, `Tests 26`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `PenarikanSaldo` connect `Tests` to `Services`, `Services 1`, `Backend 3`, `Tests 6`, `Backend 7`, `Tests 8`, `Tests 38`, `Tests 39`, `Tests 44`, `Tests 47`, `Tests 19`, `Backend 21`, `Services 22`, `Tests 23`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 51 inferred relationships involving `EnvelopeAPITestCase` (e.g. with `ActivityListTests` and `AuditLogListTests`) actually correct?**
  _`EnvelopeAPITestCase` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `KategoriSampah` (e.g. with `Command` and `get_inventory_history()`) actually correct?**
  _`KategoriSampah` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `TransaksiSetoran` (e.g. with `Meta` and `TransaksiSetoranFilter`) actually correct?**
  _`TransaksiSetoran` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `User` (e.g. with `Command` and `InsufficientPoinError`) actually correct?**
  _`User` has 7 INFERRED edges - model-reasoned connections that need verification._