# Graph Report - backend  (2026-07-08)

## Corpus Check
- 68 files · ~36,797 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 787 nodes · 1370 edges · 70 communities (46 shown, 24 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 254 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9291375e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]

## God Nodes (most connected - your core abstractions)
1. `EnvelopeAPITestCase` - 35 edges
2. `Command` - 29 edges
3. `AlreadyProcessedError` - 28 edges
4. `User` - 28 edges
5. `KategoriSampah` - 28 edges
6. `success_response()` - 26 edges
7. `Reward` - 21 edges
8. `TransaksiSetoran` - 18 edges
9. `IsOwnerOrAdmin` - 18 edges
10. `LedgerServiceTests` - 18 edges

## Surprising Connections (you probably didn't know these)
- `Meta` --uses--> `TransaksiSetoran`  [INFERRED]
  api/filters.py → api/models.py
- `DetailSetoranSerializer` --uses--> `AlreadyProcessedError`  [INFERRED]
  api/serializers.py → api/exceptions.py
- `Meta` --uses--> `AlreadyProcessedError`  [INFERRED]
  api/serializers.py → api/exceptions.py
- `MitraPengepulSerializer` --uses--> `AlreadyProcessedError`  [INFERRED]
  api/serializers.py → api/exceptions.py
- `PenarikanSaldoCreateSerializer` --uses--> `AlreadyProcessedError`  [INFERRED]
  api/serializers.py → api/exceptions.py

## Import Cycles
- 1-file cycle: `api/services/pickups.py -> api/services/pickups.py`
- 1-file cycle: `api/services/deposits.py -> api/services/deposits.py`
- 1-file cycle: `api/services/ledger.py -> api/services/ledger.py`
- 1-file cycle: `api/services/withdrawals.py -> api/services/withdrawals.py`

## Communities (70 total, 24 thin omitted)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (24): 05 — Business Rules & SOPs, A.1 Konversi Setoran ke Saldo, A.2 Konversi Saldo ke Poin Reward, A.3 Penarikan Saldo, A.4 Penukaran Poin, A. Aturan Keuangan, B.1 Setor Langsung (di Kantor), B.2 Penjemputan (via Aplikasi) (+16 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (24): Meta, TransaksiSetoranFilter, IsAdmin, IsAdminOrKoordinator, IsNasabah, IsOwnerOrAdmin, IsPetugasOrAdmin, IsPickupManager (+16 more)

### Community 3 - "Community 3"
Cohesion: 0.22
Nodes (9): Post-Launch — Fase 8, Sprint 1 (Minggu 1) — Fase 1, Sprint 2 (Minggu 2) — Fase 2.1–2.2, Sprint 3 (Minggu 3) — Fase 2.3–2.5, Sprint 4 (Minggu 4) — Fase 2.6–3, Sprint 5 (Minggu 5) — Fase 4, Sprint 6 (Minggu 6) — Fase 5–6, Sprint 7 (Minggu 7) — Fase 7 (+1 more)

### Community 8 - "Community 8"
Cohesion: 0.14
Nodes (13): 1. Extend `EnvelopeAPITestCase`, 2. Assert JSON Envelope (required), 3. File Organization, 4. What to Test per Feature, 5. Use English Routes, 6. Seed Data for Manual / Integration Tests, Do Not, MIRU Backend Feature Testing (+5 more)

### Community 10 - "Community 10"
Cohesion: 0.33
Nodes (5): graphify, Hook-Based Usage, Installation Verification, Meta Commands (always use rtk directly), RTK - Rust Token Killer

### Community 11 - "Community 11"
Cohesion: 0.40
Nodes (4): Graphify Knowledge Graph, MIRU Backend API — Agent Rules, Stack, Token Savers (WAJIB)

### Community 12 - "Community 12"
Cohesion: 0.40
Nodes (4): ⚠️ AI Steering — baca on-demand (jangan semua sekaligus), Aturan Keras, graphify, MIRU Bank Sampah — Backend API (Django)

### Community 13 - "Community 13"
Cohesion: 0.04
Nodes (48): 04 — API Contracts & Standards, 10. Mapping Role → Endpoint Access, 11. Catatan Implementasi, 1.1 Route Naming (English, kebab-case), 1. Prinsip Desain API, 2.1 Login, 2.2 Refresh Token, 2.3 Profil User Login (+40 more)

### Community 14 - "Community 14"
Cohesion: 0.08
Nodes (51): AbstractUser, DetailSetoran, KategoriSampah, MitraPengepul, PenarikanSaldo, Pengaduan, Penjemputan, PenjualanMitra (+43 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (16): 1. Environment Variables, 1. Setup Environment, 2. Build and Run, 2. Run Migrations & Server, 3. Run Migrations in Docker, 4. Seed Demo Data, 5. Run Tests, API Access & Documentation (+8 more)

### Community 16 - "Community 16"
Cohesion: 0.22
Nodes (9): 2.1 Integritas Data Transaksional, 2.2 Transaksi Setoran (Modul 6, 8, 9), 2.3 Penjemputan Workflow (Modul 7), 2.4 Penarikan Saldo (Modul 10), 2.5 Penukaran Poin (Modul 11), 2.6 Penjualan Mitra & Stok (Modul 12–13), 2.7 Pengaduan (Modul 14), 2.8 Permission & Queryset per Role (+1 more)

### Community 17 - "Community 17"
Cohesion: 0.22
Nodes (8): TransaksiSetoranSerializer, Decimal, User, build_detail_data(), prepare_details_data(), Business rules and price calculation for deposit transactions., validate_nasabah_for_setoran(), validate_petugas_for_setoran()

### Community 18 - "Community 18"
Cohesion: 0.10
Nodes (19): 07 — Modules & Features (Backend), 17 Modul Sistem — Peran Backend, Detail Endpoint Backend per Modul, Modul 10: Penarikan Saldo, Modul 11: Poin & Reward, Modul 12: Stok Gudang, Modul 13: Penjualan ke Mitra, Modul 14: Pengaduan (+11 more)

### Community 19 - "Community 19"
Cohesion: 0.25
Nodes (8): 3.1 Alur Setor Langsung (SOP B.1), 3.2 Alur Penjemputan (SOP B.2), 3.3 Alur Penarikan (SOP A.3), 3.4 Alur Penukaran Poin (SOP A.4), 3.5 Riwayat Transaksi Gabungan (Modul 9), 3.6 Profil & Kartu Digital (Modul 3), 3.7 Reward Katalog (Modul 11), Fase 3: MVP — Operasional Harian (End-to-End)

### Community 20 - "Community 20"
Cohesion: 0.29
Nodes (7): 1.1 Konfigurasi & Keamanan Dasar ✅, 1.2 Standar API Response — JSON Envelope ✅, 1.3 Autentikasi & Registrasi (Modul 2) ✅, 1.4 Manajemen Pengguna (Modul 1) ✅, 1.5 Seed Data (Modul 4–5) ✅, 1.6 Kategori Sampah (Modul 4–5) ✅, Fase 1: MVP — Infrastruktur & Auth

### Community 21 - "Community 21"
Cohesion: 0.33
Nodes (6): 7.1 Keamanan, 7.2 Deployment, 7.3 Backup & Recovery, 7.4 Monitoring & Logging, 7.5 Performance, Fase 7: Production Ready

### Community 24 - "Community 24"
Cohesion: 0.16
Nodes (15): AlreadyProcessedError, DetailSetoranReadSerializer, DetailSetoranSerializer, DetailSetoranWriteSerializer, KategoriSampahSerializer, Meta, MitraPengepulSerializer, PenarikanSaldoUpdateSerializer (+7 more)

### Community 30 - "Community 30"
Cohesion: 0.22
Nodes (13): InvalidStatusTransitionError, PenjemputanUpdateSerializer, Decimal, User, APIException, Penjemputan, Pickup request validation and status state machine., validate_estimasi_berat() (+5 more)

### Community 32 - "Community 32"
Cohesion: 0.20
Nodes (3): APITestCase, EnvelopeAPITestCase, Base test case with envelope helpers and user factories.

### Community 33 - "Community 33"
Cohesion: 0.15
Nodes (3): LoginTests, RefreshTokenTests, RegistrationTests

### Community 35 - "Community 35"
Cohesion: 0.33
Nodes (5): 08 — Task List: Backend Development Roadmap, Cakupan 17 Modul Backend, Definisi "Selesai" per Tahap, Gap Kode vs Dokumen (perlu ditangani), Ringkasan Fase

### Community 36 - "Community 36"
Cohesion: 0.33
Nodes (6): 5.1 Audit Log (Modul 17), 5.2 Pengaturan Institusi (Modul 17), 5.3 Riwayat Harga (Modul 5 — opsional MVP), 5.4 Role Pemerintah Distrik, 5.5 Kebijakan Data Pribadi (UU PDP), Fase 5: MVP Lengkap — Governance

### Community 42 - "Community 42"
Cohesion: 0.09
Nodes (28): MeView, MiruTokenObtainPairSerializer, MiruTokenObtainPairView, MiruTokenRefreshView, user_auth_payload(), HealthCheckView, OpenAPI / drf-spectacular configuration helpers., UserProfileSerializer (+20 more)

### Community 43 - "Community 43"
Cohesion: 0.50
Nodes (4): 0.1 Project Setup ✅, 0.2 Database Models ✅, 0.3 Core API Setup ✅, Fase 0: Foundation ✅ Selesai

### Community 44 - "Community 44"
Cohesion: 0.50
Nodes (4): 4.1 Dashboard API (Modul 15), 4.2 Laporan API (Modul 16), 4.3 Stok Gudang (Modul 12), Fase 4: MVP — Monitoring & Laporan

### Community 45 - "Community 45"
Cohesion: 0.50
Nodes (4): 6.1 Unit & Integration Tests, 6.2 API Documentation (OpenAPI), 6.3 Error Handling, Fase 6: Kualitas & Dokumentasi

### Community 46 - "Community 46"
Cohesion: 0.50
Nodes (4): 8.1 Fitur Tambahan, 8.2 Optimasi & Skalabilitas, 8.3 Yang TIDAK BOLEH Diimplementasikan (System Constraints), Fase 8: Post-MVP & Peningkatan

### Community 52 - "Community 52"
Cohesion: 0.08
Nodes (23): 09 — Data Dictionary & Reference Values (Backend), A.1 Daftar Jenis Sampah yang Diterima, A.2 Ketentuan Kategori, A. KATEGORI & HARGA SAMPAH (Seed Data), B. KATALOG REWARD (Seed Data), C.1 Konversi Setoran, C.2 Contoh Perhitungan (dari SOP), C.3 Aturan Keuangan Ringkas (+15 more)

### Community 56 - "Community 56"
Cohesion: 0.12
Nodes (15): 03 — Database Schema & ERD (Backend Django), 10. PenjualanMitra, 11. Pengaduan, 1. User (extends AbstractUser), 2. KategoriSampah, 3. TransaksiSetoran, 4. DetailSetoran, 5. Penjemputan (+7 more)

### Community 57 - "Community 57"
Cohesion: 0.13
Nodes (14): 06 — System Constraints (Batasan Sistem), 10. Publikasi Aplikasi, 11. Batasan Role, 12. Batasan Teknis Backend, 1. TIDAK ADA Integrasi Payment Gateway Otomatis, 2. TIDAK ADA GPS Live Tracking, 3. TIDAK ADA Integrasi Hardware Fisik, 4. TIDAK ADA Integrasi Dukcapil (+6 more)

### Community 58 - "Community 58"
Cohesion: 0.14
Nodes (13): 00 — System Prompt & Clean Code Rules, 10. Documentation, 1. Struktur & Organisasi, 2. Models (Django ORM), 3. Serializers, 4. Views & ViewSets, 5. Permissions, 6. Error Handling (+5 more)

### Community 59 - "Community 59"
Cohesion: 0.15
Nodes (12): 01 — Project Overview: MIRU Bank Sampah (Miru-G), 3 Repositori Sistem, 6 Role Pengguna, Indikator Keberhasilan Program, Informasi Aplikasi, Informasi Kontak & Organisasi, Jam Layanan Operasional, Latar Belakang (+4 more)

### Community 60 - "Community 60"
Cohesion: 0.27
Nodes (7): _envelope(), get_demo_user(), get_nav_groups(), _meta(), Flow-based API documentation data for MIRU Bank Sampah., FlowDocsView, TemplateView

### Community 61 - "Community 61"
Cohesion: 0.40
Nodes (9): Decimal, User, PenarikanSaldo, Business rules for saldo withdrawal requests., validate_approve_withdrawal(), validate_create_withdrawal(), validate_no_pending_withdrawal(), validate_nominal() (+1 more)

### Community 62 - "Community 62"
Cohesion: 0.44
Nodes (7): Reward, User, Business rules for reward point redemptions., validate_approve_redemption(), validate_create_redemption(), validate_poin_cukup(), validate_reward_stok()

### Community 65 - "Community 65"
Cohesion: 0.25
Nodes (7): 02 — Architecture & Tech Stack (Backend), API Documentation, Arsitektur, CORS Configuration, Environment Variables (`.env`), Struktur Folder, Tech Stack

## Knowledge Gaps
- **238 isolated node(s):** `Migration`, `Migration`, `Persona AI`, `1. Struktur & Organisasi`, `2. Models (Django ORM)` (+233 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EnvelopeAPITestCase` connect `Community 32` to `Community 64`, `Community 33`, `Community 34`, `Community 67`, `Community 68`, `Community 66`, `Community 38`, `Community 39`, `Community 40`, `Community 41`, `Community 14`, `Community 47`, `Community 51`, `Community 53`, `Community 31`, `Community 63`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `KategoriSampah` connect `Community 14` to `Community 0`, `Community 68`, `Community 41`, `Community 17`, `Community 53`, `Community 31`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `Command` connect `Community 0` to `Community 14`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `EnvelopeAPITestCase` (e.g. with `LoginTests` and `MeEndpointTests`) actually correct?**
  _`EnvelopeAPITestCase` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `Command` (e.g. with `DetailSetoran` and `KategoriSampah`) actually correct?**
  _`Command` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `AlreadyProcessedError` (e.g. with `DetailSetoranReadSerializer` and `DetailSetoranSerializer`) actually correct?**
  _`AlreadyProcessedError` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `User` (e.g. with `Decimal` and `KategoriSampah`) actually correct?**
  _`User` has 20 INFERRED edges - model-reasoned connections that need verification._