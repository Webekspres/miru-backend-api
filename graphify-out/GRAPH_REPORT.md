# Graph Report - backend  (2026-07-08)

## Corpus Check
- 64 files · ~35,393 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 585 nodes · 941 edges · 56 communities (38 shown, 18 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 145 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ef5443b9`
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

## God Nodes (most connected - your core abstractions)
1. `EnvelopeAPITestCase` - 29 edges
2. `Decimal` - 23 edges
3. `Command` - 18 edges
4. `Detail Endpoint Backend per Modul` - 17 edges
5. `IsAdminOrKoordinator` - 16 edges
6. `IsOwnerOrAdmin` - 16 edges
7. `IsUserOwnerOrAdmin` - 16 edges
8. `UserViewSet` - 16 edges
9. `PenjemputanViewSet` - 16 edges
10. `6. Spesifikasi Endpoint Lengkap` - 15 edges

## Surprising Connections (you probably didn't know these)
- `TransaksiSetoranFilter` --uses--> `TransaksiSetoran`  [INFERRED]
  api/filters.py → api/models.py
- `Meta` --uses--> `TransaksiSetoran`  [INFERRED]
  api/filters.py → api/models.py
- `Decimal` --uses--> `User`  [INFERRED]
  api/services/pickups.py → api/models.py
- `User` --uses--> `User`  [INFERRED]
  api/services/pickups.py → api/models.py
- `Penjemputan` --uses--> `User`  [INFERRED]
  api/services/pickups.py → api/models.py

## Import Cycles
- 1-file cycle: `api/services/pickups.py -> api/services/pickups.py`
- 1-file cycle: `api/services/deposits.py -> api/services/deposits.py`
- 1-file cycle: `api/services/ledger.py -> api/services/ledger.py`

## Communities (56 total, 18 thin omitted)

### Community 1 - "Community 1"
Cohesion: 0.19
Nodes (9): Meta, DetailSetoran, MitraPengepul, PenarikanSaldo, Pengaduan, PenjualanMitra, PenukaranPoin, Reward (+1 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (20): TransaksiSetoranFilter, IsAdmin, IsAdminOrKoordinator, IsNasabah, IsOwnerOrAdmin, IsPetugasOrAdmin, IsPickupManager, IsUserOwnerOrAdmin (+12 more)

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
Cohesion: 0.12
Nodes (28): Decimal, create_setoran_with_side_effects(), credit_nasabah_setoran(), debit_nasabah_poin(), debit_nasabah_saldo(), decrease_kategori_stok(), _ensure_non_negative_poin(), _ensure_non_negative_saldo() (+20 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (16): 1. Environment Variables, 1. Setup Environment, 2. Build and Run, 2. Run Migrations & Server, 3. Run Migrations in Docker, 4. Seed Demo Data, 5. Run Tests, API Access & Documentation (+8 more)

### Community 16 - "Community 16"
Cohesion: 0.22
Nodes (9): 2.1 Integritas Data Transaksional, 2.2 Transaksi Setoran (Modul 6, 8, 9), 2.3 Penjemputan Workflow (Modul 7), 2.4 Penarikan Saldo (Modul 10), 2.5 Penukaran Poin (Modul 11), 2.6 Penjualan Mitra & Stok (Modul 12–13), 2.7 Pengaduan (Modul 14), 2.8 Permission & Queryset per Role (+1 more)

### Community 17 - "Community 17"
Cohesion: 0.20
Nodes (12): AbstractUser, KategoriSampah, User, TransaksiSetoranSerializer, Decimal, User, KategoriSampah, build_detail_data() (+4 more)

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
Cohesion: 0.12
Nodes (12): DetailSetoranSerializer, DetailSetoranWriteSerializer, KategoriSampahSerializer, Meta, MitraPengepulSerializer, PenarikanSaldoSerializer, PengaduanSerializer, PenjualanMitraSerializer (+4 more)

### Community 30 - "Community 30"
Cohesion: 0.23
Nodes (12): InvalidStatusTransitionError, Penjemputan, PenjemputanUpdateSerializer, Decimal, User, APIException, Penjemputan, Pickup request validation and status state machine. (+4 more)

### Community 32 - "Community 32"
Cohesion: 0.14
Nodes (4): APITestCase, EnvelopeAPITestCase, Base test case with envelope helpers and user factories., WasteCategoryPublicReadTests

### Community 33 - "Community 33"
Cohesion: 0.15
Nodes (3): LoginTests, RefreshTokenTests, RegistrationTests

### Community 35 - "Community 35"
Cohesion: 0.33
Nodes (5): 08 — Task List: Backend Development Roadmap, Cakupan 17 Modul Backend, Definisi "Selesai" per Tahap, Gap Kode vs Dokumen (perlu ditangani), Ringkasan Fase

### Community 36 - "Community 36"
Cohesion: 0.33
Nodes (6): 5.1 Audit Log (Modul 17), 5.2 Pengaturan Institusi (Modul 17), 5.3 Riwayat Harga (Modul 5 — opsional MVP), 5.4 Role Pemerintah Distrik, 5.5 Kebijakan Data Pribadi (UU PDP), Fase 5: MVP Lengkap — Governance

### Community 37 - "Community 37"
Cohesion: 0.15
Nodes (3): DetailSetoranReadSerializer, UserAdminSerializer, UserRegistrationSerializer

### Community 42 - "Community 42"
Cohesion: 0.07
Nodes (36): MeView, MiruTokenObtainPairSerializer, MiruTokenObtainPairView, MiruTokenRefreshView, user_auth_payload(), _envelope(), get_demo_user(), get_nav_groups() (+28 more)

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
Cohesion: 0.33
Nodes (3): TestCase, SeedDataFullTests, SeedDataMinimalTests

## Knowledge Gaps
- **162 isolated node(s):** `Cakupan 17 Modul Backend`, `Gap Kode vs Dokumen (perlu ditangani)`, `0.1 Project Setup ✅`, `0.2 Database Models ✅`, `0.3 Core API Setup ✅` (+157 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EnvelopeAPITestCase` connect `Community 32` to `Community 33`, `Community 1`, `Community 34`, `Community 38`, `Community 39`, `Community 40`, `Community 41`, `Community 47`, `Community 51`, `Community 53`, `Community 31`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `Decimal` connect `Community 14` to `Community 32`, `Community 1`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `Command` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `EnvelopeAPITestCase` (e.g. with `LoginTests` and `MeEndpointTests`) actually correct?**
  _`EnvelopeAPITestCase` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `Decimal` (e.g. with `.setUp()` and `.test_create_setoran_with_side_effects_atomically()`) actually correct?**
  _`Decimal` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `IsAdminOrKoordinator` (e.g. with `KategoriSampahViewSet` and `MitraPengepulViewSet`) actually correct?**
  _`IsAdminOrKoordinator` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Cakupan 17 Modul Backend`, `Gap Kode vs Dokumen (perlu ditangani)`, `0.1 Project Setup ✅` to the rest of the system?**
  _181 weakly-connected nodes found - possible documentation gaps or missing edges._