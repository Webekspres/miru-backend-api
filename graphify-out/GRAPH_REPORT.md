# Graph Report - backend  (2026-07-07)

## Corpus Check
- 41 files · ~18,569 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 279 nodes · 297 edges · 30 communities (24 shown, 6 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 5 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d4ae4021`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
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

## God Nodes (most connected - your core abstractions)
1. `Detail Endpoint Backend per Modul` - 17 edges
2. `6. Spesifikasi Endpoint Lengkap` - 15 edges
3. `08 — Task List: Backend Development Roadmap` - 13 edges
4. `04 — API Contracts & Standards` - 12 edges
5. `3. Format Response Standar Industri — JSON Envelope` - 11 edges
6. `success_envelope()` - 10 edges
7. `Fase 2: MVP — Logika Bisnis Inti` - 9 edges
8. `Urutan Pengerjaan Rekomendasi (Sprint)` - 9 edges
9. `Fase 3: MVP — Operasional Harian (End-to-End)` - 8 edges
10. `error_envelope()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `MiruTokenObtainPairSerializer` --uses--> `Response`  [INFERRED]
  api/auth_views.py → api/utils/response.py
- `MiruTokenObtainPairView` --uses--> `Response`  [INFERRED]
  api/auth_views.py → api/utils/response.py
- `MiruTokenRefreshView` --uses--> `Response`  [INFERRED]
  api/auth_views.py → api/utils/response.py
- `MiruPagination` --uses--> `Response`  [INFERRED]
  api/utils/pagination.py → api/utils/response.py
- `miru_exception_handler()` --calls--> `error_envelope()`  [EXTRACTED]
  api/utils/exception_handler.py → api/utils/response.py

## Import Cycles
- None detected.

## Communities (30 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (12): DetailSetoranSerializer, KategoriSampahSerializer, Meta, MitraPengepulSerializer, PenarikanSaldoSerializer, PengaduanSerializer, PenjemputanSerializer, PenjualanMitraSerializer (+4 more)

### Community 1 - "Community 1"
Cohesion: 0.15
Nodes (12): AbstractUser, DetailSetoran, KategoriSampah, MitraPengepul, PenarikanSaldo, Pengaduan, Penjemputan, PenjualanMitra (+4 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (13): IsAdminOrKoordinator, IsOwnerOrAdmin, IsPetugasOrAdmin, KategoriSampahViewSet, MitraPengepulViewSet, PenarikanSaldoViewSet, PengaduanViewSet, PenjemputanViewSet (+5 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (36): 08 — Task List: Backend Development Roadmap, 0.1 Project Setup ✅, 0.2 Database Models ✅, 0.3 Core API Setup ✅, 4.1 Dashboard API (Modul 15), 4.2 Laporan API (Modul 16), 4.3 Stok Gudang (Modul 12), 5.1 Audit Log (Modul 17) (+28 more)

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
Cohesion: 0.09
Nodes (22): 04 — API Contracts & Standards, 10. Mapping Role → Endpoint Access, 11. Catatan Implementasi, 1.1 Route Naming (English, kebab-case), 1. Prinsip Desain API, 2.1 Login, 2.2 Refresh Token, 2.3 Profil User Login (+14 more)

### Community 14 - "Community 14"
Cohesion: 0.13
Nodes (15): 6.10 Riwayat Transaksi Gabungan, 6.11 Dashboard, 6.12 Laporan, 6.13 Pengaturan Institusi, 6.14 Audit Log, 6.1 Health Check, 6.2 Users — Manajemen Pengguna, 6.3 Kategori Sampah (+7 more)

### Community 15 - "Community 15"
Cohesion: 0.17
Nodes (11): 1. Environment Variables, 1. Setup Environment, 2. Build and Run, 2. Run Migrations & Server, 3. Run Migrations in Docker, API Access & Documentation, API Routes (English), Authentication (+3 more)

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
Nodes (7): 1.1 Konfigurasi & Keamanan Dasar ✅, 1.2 Standar API Response — JSON Envelope ✅, 1.3 Autentikasi & Registrasi (Modul 2), 1.4 Manajemen Pengguna (Modul 1), 1.5 Seed Data (Modul 4–5), 1.6 Kategori Sampah (Modul 4–5), Fase 1: MVP — Infrastruktur & Auth

### Community 21 - "Community 21"
Cohesion: 0.33
Nodes (6): 7.1 Keamanan, 7.2 Deployment, 7.3 Backup & Recovery, 7.4 Monitoring & Logging, 7.5 Performance, Fase 7: Production Ready

### Community 24 - "Community 24"
Cohesion: 0.10
Nodes (25): MiruTokenObtainPairSerializer, MiruTokenObtainPairView, MiruTokenRefreshView, HealthCheckView, APIView, JSONRenderer, PageNumberPagination, Response (+17 more)

## Knowledge Gaps
- **154 isolated node(s):** `1.1 Route Naming (English, kebab-case)`, `2.1 Login`, `2.2 Refresh Token`, `2.3 Profil User Login`, `2.4 Header Autentikasi` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `08 — Task List: Backend Development Roadmap` connect `Community 3` to `Community 16`, `Community 19`, `Community 20`, `Community 21`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `04 — API Contracts & Standards` connect `Community 13` to `Community 17`, `Community 14`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `6. Spesifikasi Endpoint Lengkap` connect `Community 14` to `Community 13`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **What connects `1.1 Route Naming (English, kebab-case)`, `2.1 Login`, `2.2 Refresh Token` to the rest of the system?**
  _158 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.09333333333333334 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.05405405405405406 - nodes in this community are weakly interconnected._