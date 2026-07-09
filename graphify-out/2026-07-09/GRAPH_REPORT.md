# Graph Report - .  (2026-07-09)

## Corpus Check
- Corpus is ~48,110 words - fits in a single context window. You may not need a graph.

## Summary
- 1053 nodes · 2438 edges · 95 communities (45 shown, 50 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 512 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

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
- `graphify Knowledge Graph` --conceptually_related_to--> `MIRU Bank Sampah (Miru-G)`  [INFERRED]
  AGENTS.md → .ai-steering/01-project-overview.md
- `Docker Compose Django Web Service` --implements--> `Django REST API Backend`  [INFERRED]
  docker-compose.yml → .ai-steering/02-architecture-and-stack.md
- `GET/POST /api/deposits/` --references--> `API /api/deposits/`  [EXTRACTED]
  README.md → .ai-steering/04-api-contracts-and-standards.md
- `GET/POST /api/pickups/` --references--> `API /api/pickups/`  [EXTRACTED]
  README.md → .ai-steering/04-api-contracts-and-standards.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Deposit Transaction Flow (setoran → saldo + poin + stok)** — _ai_steering_04_api_contracts_and_standards_api_deposits, _ai_steering_03_database_schema_erd_transaksisetoran, _ai_steering_03_database_schema_erd_detailsetoran, _ai_steering_03_database_schema_erd_nasabah_saldo_ledger, _ai_steering_03_database_schema_erd_nasabah_poin_ledger, _ai_steering_03_database_schema_erd_kategorisampah [EXTRACTED 1.00]
- **Pickup Status Workflow (menunggu → selesai / ditolak)** — _ai_steering_04_api_contracts_and_standards_api_pickups, _ai_steering_03_database_schema_erd_penjemputan, _ai_steering_05_business_rules_sops_pickup_status_flow, _ai_steering_06_system_constraints_no_gps_tracking [EXTRACTED 1.00]
- **MIRU Six User Roles** — _ai_steering_01_project_overview_role_nasabah, _ai_steering_01_project_overview_role_petugas, _ai_steering_01_project_overview_role_admin, _ai_steering_01_project_overview_role_koordinator, _ai_steering_01_project_overview_role_pemerintah, _ai_steering_01_project_overview_role_mitra [EXTRACTED 1.00]

## Communities (95 total, 50 thin omitted)

### Community 0 - "Services"
Cohesion: 0.08
Nodes (43): PenjualanMitra, PenjualanMitraCreateSerializer, adjust_setoran_correction(), complete_penukaran_poin(), create_setoran_with_side_effects(), credit_nasabah_setoran(), debit_nasabah_poin(), debit_nasabah_saldo() (+35 more)

### Community 1 - "Services 1"
Cohesion: 0.09
Nodes (49): DashboardDepositChartView, DashboardOverviewView, DashboardRecentActivityView, InventoryHistoryView, InventoryView, MonitorView, Monitoring endpoints: dashboard (Modul 15), laporan (Modul 16), inventory (Modul, Base view for admin/koordinator/pemerintah read-only monitoring. (+41 more)

### Community 2 - "Backend"
Cohesion: 0.07
Nodes (32): MeView, MiruTokenObtainPairSerializer, MiruTokenObtainPairView, MiruTokenRefreshView, user_auth_payload(), _envelope(), get_demo_user(), get_nav_groups() (+24 more)

### Community 3 - "Backend 3"
Cohesion: 0.06
Nodes (11): PengaturanInstitusiAdmin, PengumumanAdmin, RiwayatHargaAdmin, Command, PengaturanInstitusi, Pengumuman, Singleton — profil institusi bank sampah (pk selalu 1)., RiwayatHarga (+3 more)

### Community 4 - "Tests"
Cohesion: 0.12
Nodes (12): PenarikanSaldo, Pengaduan, Penjemputan, PenukaranPoin, Reward, DashboardDepositChartTests, DashboardOverviewTests, DashboardRecentActivityTests (+4 more)

### Community 5 - "Docs"
Cohesion: 0.06
Nodes (35): Role: Admin Aplikasi, Role: Mitra/Pengepul, Role: Nasabah, Role: Pemerintah Distrik, Role: Petugas Bank Sampah, DetailSetoran Model, KategoriSampah Model, MitraPengepul Model (+27 more)

### Community 6 - "Tests 6"
Cohesion: 0.11
Nodes (8): TransaksiSetoran, DailyReportTests, EvaluationReportTests, MonthlyReportTests, ReportTestMixin, WasteReportTests, WeeklyReportTests, datetime

### Community 7 - "Backend 7"
Cohesion: 0.13
Nodes (25): get_client_ip(), get_current_request(), get_current_user(), Get the current user from thread-local storage., Extract client IP from request headers., Access the current request from thread-local storage (for signals etc.)., audit_post_delete(), audit_post_save() (+17 more)

### Community 8 - "Tests 8"
Cohesion: 0.15
Nodes (5): Meta, MitraPengepul, EnvelopeAPITestCase, Base test case with envelope helpers and user factories., APITestCase

### Community 9 - "Backend 9"
Cohesion: 0.12
Nodes (15): AlreadyProcessedError, DetailSetoranReadSerializer, DetailSetoranSerializer, DetailSetoranWriteSerializer, Meta, MitraPengepulSerializer, NasabahLookupSerializer, PenarikanSaldoCreateSerializer (+7 more)

### Community 10 - "Backend 10"
Cohesion: 0.15
Nodes (8): IsAdmin, IsNasabah, IsOwnerOrAdmin, IsPemerintahReadOnly, IsPickupManager, Pemerintah distrik: hanya boleh akses read (GET/HEAD/OPTIONS)., PengaduanViewSet, RewardViewSet

### Community 11 - "Tests 11"
Cohesion: 0.10
Nodes (5): LoginTests, MeEndpointTests, PrivacyPolicyTests, RefreshTokenTests, RegistrationTests

### Community 12 - "Tests 12"
Cohesion: 0.08
Nodes (4): AdminCreateStaffTests, UserListFilterTests, UserPatchPermissionTests, UserResponseSecurityTests

### Community 13 - "Tests 13"
Cohesion: 0.09
Nodes (5): AuditLog, AuditLogListTests, AuditLogSignalTests, DepositCorrectionTests, Verify automatic audit log recording via Django signals.

### Community 14 - "Backend 14"
Cohesion: 0.16
Nodes (12): PengaturanInstitusiSerializer, PengumumanSerializer, get_privacy_policy(), Kebijakan data pribadi (UU PDP) — konten untuk API publik., get_institution_settings(), Institution settings singleton helpers., Return the singleton institution settings row (creates defaults if missing)., InstitutionSettingsView (+4 more)

### Community 15 - "Services 15"
Cohesion: 0.16
Nodes (14): InvalidStatusTransitionError, PickupAssignSerializer, approve_pickup(), assign_pickup(), Decimal, Pickup request validation and status state machine., reject_pickup(), update_pickup_status() (+6 more)

### Community 16 - "Backend 16"
Cohesion: 0.15
Nodes (4): PenukaranPoinSerializer, success_response(), KategoriSampahViewSet, PenukaranPoinViewSet

### Community 17 - "Backend 17"
Cohesion: 0.21
Nodes (10): Meta, TransaksiSetoranFilter, IsActivityReader, IsStaffManagerOrPetugas, IsUserOwnerOrAdmin, Object-level permission for the User model (/api/users/{id}/)., Admin, koordinator, atau petugas — untuk lookup nasabah., Nasabah (milik sendiri) atau staff read-all untuk riwayat gabungan. (+2 more)

### Community 18 - "Backend 18"
Cohesion: 0.14
Nodes (3): PenjualanMitraSerializer, UserAdminSerializer, PenjualanMitraViewSet

### Community 20 - "Services 20"
Cohesion: 0.17
Nodes (9): TransaksiSetoranCreateSerializer, build_bukti_digital(), build_detail_data(), prepare_details_data(), Decimal, Business rules and price calculation for deposit transactions., Struktur bukti digital untuk nasabah (SOP B.1)., validate_nasabah_for_setoran() (+1 more)

### Community 21 - "Backend 21"
Cohesion: 0.22
Nodes (6): filter_nasabah_owned(), filter_pickup_queryset(), filter_staff_only(), Reusable queryset filters per role., Admin/koordinator/pemerintah read; others denied., Nasabah sees own data; staff roles see all.

### Community 22 - "Services 22"
Cohesion: 0.28
Nodes (11): approve_withdrawal(), _ensure_pending(), Decimal, Business rules for saldo withdrawal requests., Tolak pengajuan — saldo tidak pernah didebit saat create, jadi tidak perlu refun, reject_withdrawal(), validate_approve_withdrawal(), validate_create_withdrawal() (+3 more)

### Community 24 - "Tests 24"
Cohesion: 0.21
Nodes (5): KategoriSampah, SeedDataFullTests, SeedDataMinimalTests, WasteCategoryPublicReadTests, TestCase

### Community 25 - "Backend 25"
Cohesion: 0.21
Nodes (4): IsAdminOrKoordinator, IsMonitorReadOnly, Admin, koordinator, pemerintah — akses read untuk monitoring., MitraPengepulViewSet

### Community 28 - "Services 28"
Cohesion: 0.36
Nodes (9): AbstractUser, User, get_activity_items(), _penarikan_items(), _penukaran_items(), Merged transaction history for nasabah activity feed., _resolve_nasabah_filter(), _setoran_items() (+1 more)

### Community 29 - "Backend 29"
Cohesion: 0.27
Nodes (3): IsPetugasOrAdmin, TransaksiSetoranReadSerializer, TransaksiSetoranViewSet

### Community 30 - "Backend 30"
Cohesion: 0.22
Nodes (6): AuditLogSerializer, RiwayatHargaSerializer, get_price_history(), Return price history queryset for a category., MiruPagination, PageNumberPagination

### Community 31 - "Backend 31"
Cohesion: 0.20
Nodes (3): KategoriSampahSerializer, Admin-only: koreksi data transaksi setoran., TransaksiSetoranCorrectionSerializer

### Community 33 - "Backend 33"
Cohesion: 0.20
Nodes (5): PengaduanSerializer, PengaduanUpdateSerializer, Business rules for nasabah complaints., validate_admin_close(), validate_jenis_pengaduan()

### Community 41 - "Backend 41"
Cohesion: 0.25
Nodes (3): PenjemputanCreateSerializer, PenjemputanUpdateSerializer, validate_jadwal_h_plus_one()

### Community 42 - "Services 42"
Cohesion: 0.43
Nodes (7): approve_redemption(), _ensure_pending(), Business rules for reward point redemptions., validate_approve_redemption(), validate_create_redemption(), validate_poin_cukup(), validate_reward_stok()

### Community 48 - "Services 48"
Cohesion: 0.43
Nodes (5): DetailSetoran, Shared aggregation helpers for dashboard and report endpoints., stok_per_kategori(), get_overview(), Aggregated data for the monitoring dashboard (Modul 15).

### Community 58 - "Services 58"
Cohesion: 0.50
Nodes (4): Decimal, Price change history for waste categories., Record a price change when harga_beli_per_kg is updated., record_price_change()

### Community 60 - "Misc"
Cohesion: 0.90
Nodes (4): handle(), main(), pipe(), socket

### Community 61 - "Docs 61"
Cohesion: 0.50
Nodes (4): MIRU Bank Sampah (Miru-G), Django REST API Backend, graphify Knowledge Graph, Docker Compose Django Web Service

### Community 65 - "Docs 65"
Cohesion: 0.67
Nodes (3): JWT Auth (djangorestframework-simplejwt), API /api/auth/login/, djangorestframework-simplejwt Dependency

## Knowledge Gaps
- **37 isolated node(s):** `Migration`, `Migration`, `Migration`, `Migration`, `Migration` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **50 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EnvelopeAPITestCase` connect `Tests 8` to `Backend 3`, `Tests`, `Tests 6`, `Tests 11`, `Tests 12`, `Tests 13`, `Tests 19`, `Tests 23`, `Tests 24`, `Tests 26`, `Tests 27`, `Tests 34`, `Tests 35`, `Tests 36`, `Tests 37`, `Tests 38`, `Tests 39`, `Tests 43`, `Tests 44`, `Tests 45`, `Tests 46`, `Tests 47`, `Tests 51`, `Tests 52`, `Tests 53`, `Tests 54`, `Tests 55`, `Tests 56`, `Tests 59`, `Tests 64`?**
  _High betweenness centrality (0.177) - this node is a cross-community bridge._
- **Why does `KategoriSampah` connect `Tests 24` to `Services`, `Services 1`, `Backend 3`, `Tests`, `Tests 6`, `Backend 7`, `Tests 8`, `Tests 13`, `Tests 19`, `Services 20`, `Tests 23`, `Tests 26`, `Tests 34`, `Tests 35`, `Tests 44`, `Services 48`, `Tests 51`, `Tests 52`, `Tests 55`, `Services 58`, `Tests 59`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Why does `TransaksiSetoran` connect `Tests 6` to `Services`, `Services 1`, `Backend 3`, `Tests`, `Backend 7`, `Tests 8`, `Tests 44`, `Tests 13`, `Services 48`, `Backend 17`, `Tests 51`, `Tests 52`, `Tests 19`, `Tests 23`, `Tests 26`, `Tests 59`, `Services 28`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 51 inferred relationships involving `EnvelopeAPITestCase` (e.g. with `ActivityListTests` and `AuditLogListTests`) actually correct?**
  _`EnvelopeAPITestCase` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `KategoriSampah` (e.g. with `Command` and `get_inventory_history()`) actually correct?**
  _`KategoriSampah` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `TransaksiSetoran` (e.g. with `Meta` and `TransaksiSetoranFilter`) actually correct?**
  _`TransaksiSetoran` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `User` (e.g. with `Command` and `InsufficientPoinError`) actually correct?**
  _`User` has 7 INFERRED edges - model-reasoned connections that need verification._