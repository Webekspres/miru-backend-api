# Graph Report - backend  (2026-07-07)

## Corpus Check
- 54 files · ~32,886 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 442 nodes · 564 edges · 51 communities (34 shown, 17 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 59 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0870fd6f`
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

## God Nodes (most connected - your core abstractions)
1. `EnvelopeAPITestCase` - 22 edges
2. `Command` - 18 edges
3. `Detail Endpoint Backend per Modul` - 17 edges
4. `IsAdminOrKoordinator` - 16 edges
5. `IsUserOwnerOrAdmin` - 16 edges
6. `6. Spesifikasi Endpoint Lengkap` - 15 edges
7. `IsAdmin` - 14 edges
8. `IsOwnerOrAdmin` - 14 edges
9. `08 — Task List: Backend Development Roadmap` - 13 edges
10. `UserViewSet` - 12 edges

## Surprising Connections (you probably didn't know these)
- `LoginTests` --uses--> `EnvelopeAPITestCase`  [INFERRED]
  api/tests/test_auth.py → api/tests/base.py
- `MeEndpointTests` --uses--> `EnvelopeAPITestCase`  [INFERRED]
  api/tests/test_auth.py → api/tests/base.py
- `RefreshTokenTests` --uses--> `EnvelopeAPITestCase`  [INFERRED]
  api/tests/test_auth.py → api/tests/base.py
- `RegistrationTests` --uses--> `EnvelopeAPITestCase`  [INFERRED]
  api/tests/test_auth.py → api/tests/base.py
- `AdminCreateStaffTests` --uses--> `EnvelopeAPITestCase`  [INFERRED]
  api/tests/test_users.py → api/tests/base.py

## Import Cycles
- None detected.

## Communities (51 total, 17 thin omitted)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (15): AbstractUser, DetailSetoran, KategoriSampah, MitraPengepul, PenarikanSaldo, Pengaduan, Penjemputan, PenjualanMitra (+7 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (16): IsAdmin, IsAdminOrKoordinator, IsOwnerOrAdmin, IsPetugasOrAdmin, IsUserOwnerOrAdmin, Object-level permission for the User model (/api/users/{id}/)., KategoriSampahViewSet, MitraPengepulViewSet (+8 more)

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
Cohesion: 0.05
Nodes (37): 04 — API Contracts & Standards, 10. Mapping Role → Endpoint Access, 11. Catatan Implementasi, 1.1 Route Naming (English, kebab-case), 1. Prinsip Desain API, 2.1 Login, 2.2 Refresh Token, 2.3 Profil User Login (+29 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (15): 1. Environment Variables, 1. Setup Environment, 2. Build and Run, 2. Run Migrations & Server, 3. Run Migrations in Docker, 4. Seed Demo Data, 5. Run Tests, API Access & Documentation (+7 more)

### Community 16 - "Community 16"
Cohesion: 0.22
Nodes (9): 2.1 Integritas Data Transaksional, 2.2 Transaksi Setoran (Modul 6, 8, 9), 2.3 Penjemputan Workflow (Modul 7), 2.4 Penarikan Saldo (Modul 10), 2.5 Penukaran Poin (Modul 11), 2.6 Penjualan Mitra & Stok (Modul 12–13), 2.7 Pengaduan (Modul 14), 2.8 Permission & Queryset per Role (+1 more)

### Community 17 - "Community 17"
Cohesion: 0.18
Nodes (11): 3.10 Perbandingan dengan Pola Lain, 3.1 Struktur Envelope (Semua Response), 3.2 Response Sukses — Resource Tunggal, 3.3 Response Sukses — Koleksi (Paginated), 3.4 Response Sukses — Aksi Kustom, 3.5 Response Error — Format Standar, 3.6 Kode Error Standar, 3.7 Kode Error Bisnis (Domain-Specific) (+3 more)

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
Cohesion: 0.06
Nodes (38): MeView, MiruTokenObtainPairSerializer, MiruTokenObtainPairView, MiruTokenRefreshView, user_auth_payload(), HealthCheckView, OpenAPI / drf-spectacular configuration helpers., DetailSetoranSerializer (+30 more)

### Community 30 - "Community 30"
Cohesion: 0.27
Nodes (7): _envelope(), get_demo_user(), get_nav_groups(), _meta(), Flow-based API documentation data for MIRU Bank Sampah., FlowDocsView, TemplateView

### Community 32 - "Community 32"
Cohesion: 0.22
Nodes (3): APITestCase, EnvelopeAPITestCase, Base test case with envelope helpers and user factories.

### Community 35 - "Community 35"
Cohesion: 0.33
Nodes (5): 08 — Task List: Backend Development Roadmap, Cakupan 17 Modul Backend, Definisi "Selesai" per Tahap, Gap Kode vs Dokumen (perlu ditangani), Ringkasan Fase

### Community 36 - "Community 36"
Cohesion: 0.33
Nodes (6): 5.1 Audit Log (Modul 17), 5.2 Pengaturan Institusi (Modul 17), 5.3 Riwayat Harga (Modul 5 — opsional MVP), 5.4 Role Pemerintah Distrik, 5.5 Kebijakan Data Pribadi (UU PDP), Fase 5: MVP Lengkap — Governance

### Community 42 - "Community 42"
Cohesion: 0.70
Nodes (4): _flatten_errors(), _get_error_code(), _get_error_message(), miru_exception_handler()

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

## Knowledge Gaps
- **163 isolated node(s):** `Cakupan 17 Modul Backend`, `Gap Kode vs Dokumen (perlu ditangani)`, `0.1 Project Setup ✅`, `0.2 Database Models ✅`, `0.3 Core API Setup ✅` (+158 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EnvelopeAPITestCase` connect `Community 32` to `Community 33`, `Community 34`, `Community 37`, `Community 38`, `Community 39`, `Community 40`, `Community 41`, `Community 47`, `Community 31`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `Command` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `WasteCategoryAdminCrudTests` connect `Community 31` to `Community 32`, `Community 41`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `EnvelopeAPITestCase` (e.g. with `LoginTests` and `MeEndpointTests`) actually correct?**
  _`EnvelopeAPITestCase` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `IsAdminOrKoordinator` (e.g. with `KategoriSampahViewSet` and `MitraPengepulViewSet`) actually correct?**
  _`IsAdminOrKoordinator` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `IsUserOwnerOrAdmin` (e.g. with `KategoriSampahViewSet` and `MitraPengepulViewSet`) actually correct?**
  _`IsUserOwnerOrAdmin` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Cakupan 17 Modul Backend`, `Gap Kode vs Dokumen (perlu ditangani)`, `0.1 Project Setup ✅` to the rest of the system?**
  _172 weakly-connected nodes found - possible documentation gaps or missing edges._