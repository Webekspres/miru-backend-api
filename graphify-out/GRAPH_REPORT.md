# Graph Report - backend  (2026-07-07)

## Corpus Check
- 33 files · ~10,797 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 77 nodes · 71 edges · 13 communities (11 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8c337e8b`
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

## God Nodes (most connected - your core abstractions)
1. `RTK - Rust Token Killer` - 5 edges
2. `MIRU Backend API — Agent Rules` - 4 edges
3. `graphify` - 3 edges
4. `IsAdminOrKoordinator` - 3 edges
5. `IsOwnerOrAdmin` - 3 edges
6. `ApiConfig` - 2 edges
7. `User` - 2 edges
8. `IsPetugasOrAdmin` - 2 edges
9. `UserSerializer` - 2 edges
10. `TransaksiSetoranSerializer` - 2 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (13 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (12): DetailSetoranSerializer, KategoriSampahSerializer, Meta, MitraPengepulSerializer, PenarikanSaldoSerializer, PengaduanSerializer, PenjemputanSerializer, PenjualanMitraSerializer (+4 more)

### Community 1 - "Community 1"
Cohesion: 0.15
Nodes (12): AbstractUser, DetailSetoran, KategoriSampah, MitraPengepul, PenarikanSaldo, Pengaduan, Penjemputan, PenjualanMitra (+4 more)

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (8): MitraPengepulViewSet, PenarikanSaldoViewSet, PengaduanViewSet, PenjemputanViewSet, PenjualanMitraViewSet, PenukaranPoinViewSet, RewardViewSet, TransaksiSetoranViewSet

### Community 3 - "Community 3"
Cohesion: 0.20
Nodes (5): IsAdminOrKoordinator, IsOwnerOrAdmin, IsPetugasOrAdmin, KategoriSampahViewSet, UserViewSet

### Community 10 - "Community 10"
Cohesion: 0.33
Nodes (5): graphify, Hook-Based Usage, Installation Verification, Meta Commands (always use rtk directly), RTK - Rust Token Killer

### Community 11 - "Community 11"
Cohesion: 0.40
Nodes (4): Graphify Knowledge Graph, MIRU Backend API — Agent Rules, Stack, Token Savers (WAJIB)

### Community 12 - "Community 12"
Cohesion: 0.40
Nodes (4): ⚠️ AI Steering — baca on-demand (jangan semua sekaligus), Aturan Keras, graphify, MIRU Bank Sampah — Backend API (Django)

## Knowledge Gaps
- **36 isolated node(s):** `MIRU Bank Sampah — Backend API (Django)`, `⚠️ AI Steering — baca on-demand (jangan semua sekaligus)`, `Aturan Keras`, `Token Savers (WAJIB)`, `Graphify Knowledge Graph` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `MIRU Bank Sampah — Backend API (Django)`, `⚠️ AI Steering — baca on-demand (jangan semua sekaligus)`, `Aturan Keras` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._