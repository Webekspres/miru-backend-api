# Graph Report - .  (2026-07-07)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 61 nodes · 58 edges · 10 communities (8 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `94a24e89`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]

## God Nodes (most connected - your core abstractions)
1. `IsAdminOrKoordinator` - 3 edges
2. `IsOwnerOrAdmin` - 3 edges
3. `ApiConfig` - 2 edges
4. `User` - 2 edges
5. `IsPetugasOrAdmin` - 2 edges
6. `UserSerializer` - 2 edges
7. `TransaksiSetoranSerializer` - 2 edges
8. `UserViewSet` - 2 edges
9. `KategoriSampahViewSet` - 2 edges
10. `PenarikanSaldoViewSet` - 2 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (10 total, 2 thin omitted)

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

## Knowledge Gaps
- **26 isolated node(s):** `Migration`, `KategoriSampah`, `TransaksiSetoran`, `DetailSetoran`, `Penjemputan` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Migration`, `KategoriSampah`, `TransaksiSetoran` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._