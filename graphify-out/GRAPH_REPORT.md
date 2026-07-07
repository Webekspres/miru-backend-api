# Graph Report - backend  (2026-07-07)

## Corpus Check
- 33 files · ~16,153 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 210 nodes · 195 edges · 28 communities (23 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c5f1dd6a`
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
- [[_COMMUNITY_Community 25|Community 25]]

## God Nodes (most connected - your core abstractions)
1. `6. Spesifikasi Endpoint Lengkap` - 15 edges
2. `08 — Task List: Backend Development Roadmap` - 13 edges
3. `04 — API Contracts & Standards` - 12 edges
4. `Fase 2: MVP — Logika Bisnis Inti` - 9 edges
5. `Urutan Pengerjaan Rekomendasi (Sprint)` - 9 edges
6. `Fase 3: MVP — Operasional Harian (End-to-End)` - 8 edges
7. `3. Format Response Standar Industri` - 7 edges
8. `Fase 1: MVP — Infrastruktur & Auth` - 7 edges
9. `2. Autentikasi — JWT (RFC 7519)` - 6 edges
10. `Fase 5: MVP Lengkap — Governance` - 6 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (28 total, 5 thin omitted)

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
Cohesion: 0.07
Nodes (27): 08 — Task List: Backend Development Roadmap, 0.1 Project Setup ✅, 0.2 Database Models ✅, 0.3 Core API Setup ✅, 4.1 Dashboard API (Modul 15), 4.2 Laporan API (Modul 16), 4.3 Stok Gudang (Modul 12), 6.1 Unit & Integration Tests (+19 more)

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
Nodes (21): 04 — API Contracts & Standards, 10. Mapping Role → Endpoint Access, 11. Catatan Implementasi, 1. Prinsip Desain API, 2.1 Login, 2.2 Refresh Token, 2.3 Profil User Login, 2.4 Header Autentikasi (+13 more)

### Community 14 - "Community 14"
Cohesion: 0.13
Nodes (15): 6.10 Riwayat Transaksi Gabungan, 6.11 Dashboard, 6.12 Laporan, 6.13 Pengaturan Institusi, 6.14 Audit Log, 6.1 Health Check, 6.2 Users — Manajemen Pengguna, 6.3 Kategori Sampah (+7 more)

### Community 15 - "Community 15"
Cohesion: 0.18
Nodes (10): 1. Environment Variables, 1. Setup Environment, 2. Build and Run, 2. Run Migrations & Server, 3. Run Migrations in Docker, API Access & Documentation, Authentication, Local Development (SQLite) (+2 more)

### Community 16 - "Community 16"
Cohesion: 0.22
Nodes (9): 2.1 Integritas Data Transaksional, 2.2 Transaksi Setoran (Modul 6, 8, 9), 2.3 Penjemputan Workflow (Modul 7), 2.4 Penarikan Saldo (Modul 10), 2.5 Penukaran Poin (Modul 11), 2.6 Penjualan Mitra & Stok (Modul 12–13), 2.7 Pengaduan (Modul 14), 2.8 Permission & Queryset per Role (+1 more)

### Community 17 - "Community 17"
Cohesion: 0.22
Nodes (9): Post-Launch — Fase 8, Sprint 1 (Minggu 1) — Fase 1, Sprint 2 (Minggu 2) — Fase 2.1–2.2, Sprint 3 (Minggu 3) — Fase 2.3–2.5, Sprint 4 (Minggu 4) — Fase 2.6–3, Sprint 5 (Minggu 5) — Fase 4, Sprint 6 (Minggu 6) — Fase 5–6, Sprint 7 (Minggu 7) — Fase 7 (+1 more)

### Community 18 - "Community 18"
Cohesion: 0.25
Nodes (8): 3.1 Alur Setor Langsung (SOP B.1), 3.2 Alur Penjemputan (SOP B.2), 3.3 Alur Penarikan (SOP A.3), 3.4 Alur Penukaran Poin (SOP A.4), 3.5 Riwayat Transaksi Gabungan (Modul 9), 3.6 Profil & Kartu Digital (Modul 3), 3.7 Reward Katalog (Modul 11), Fase 3: MVP — Operasional Harian (End-to-End)

### Community 19 - "Community 19"
Cohesion: 0.29
Nodes (7): 3.1 Response Sukses — Resource Tunggal, 3.2 Response Sukses — Koleksi (Paginated), 3.3 Response Sukses — Aksi Kustom, 3.4 Response Error — RFC 7807 Problem Details, 3.5 Kode Error Standar, 3.6 Kode Error Bisnis (Domain-Specific), 3. Format Response Standar Industri

### Community 20 - "Community 20"
Cohesion: 0.29
Nodes (7): 1.1 Konfigurasi & Keamanan Dasar, 1.2 Standar API Response (lihat `04-api-contracts-and-standards.md`), 1.3 Autentikasi & Registrasi (Modul 2), 1.4 Manajemen Pengguna (Modul 1), 1.5 Seed Data (Modul 4–5), 1.6 Kategori Sampah (Modul 4–5), Fase 1: MVP — Infrastruktur & Auth

### Community 21 - "Community 21"
Cohesion: 0.33
Nodes (6): 5.1 Audit Log (Modul 17), 5.2 Pengaturan Institusi (Modul 17), 5.3 Riwayat Harga (Modul 5 — opsional MVP), 5.4 Role Pemerintah Distrik, 5.5 Kebijakan Data Pribadi (UU PDP), Fase 5: MVP Lengkap — Governance

## Knowledge Gaps
- **133 isolated node(s):** `1. Prinsip Desain API`, `2.1 Login`, `2.2 Refresh Token`, `2.3 Profil User Login`, `2.4 Header Autentikasi` (+128 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `08 — Task List: Backend Development Roadmap` connect `Community 3` to `Community 16`, `Community 17`, `Community 18`, `Community 20`, `Community 21`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `04 — API Contracts & Standards` connect `Community 13` to `Community 19`, `Community 14`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `6. Spesifikasi Endpoint Lengkap` connect `Community 14` to `Community 13`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **What connects `1. Prinsip Desain API`, `2.1 Login`, `2.2 Refresh Token` to the rest of the system?**
  _136 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.09420289855072464 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.07142857142857142 - nodes in this community are weakly interconnected._