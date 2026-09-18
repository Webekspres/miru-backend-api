# Graph Report - backend  (2026-09-17)

## Corpus Check
- 172 files · ~100,111 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2343 nodes · 4427 edges · 166 communities (93 shown, 62 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 441 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c453f5d6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Penjemputan
- reports.py
- delete_account_views.py
- 11 — Security & Privacy (Backend — Sumber Kanonik)
- signals.py
- API Flow Guide (/api/guide/)
- PhoneOTP
- InventoryHistoryTests
- User
- EnvelopeAPITestCase
- _backup_lib.sh
- monitoring_views.py
- whatsapp.py
- ReportTestMixin
- PengaturanInstitusi
- UserRegistrationSerializer
- openapi.py
- ledger.py
- ExportBaseView
- excel_export.py
- MonitorView
- DeleteAccountTests
- KontenEdukasi
- PriceHistoryTests
- ♻
- flow_docs_data.py
- KontenEdukasiSerializer
- DashboardOverviewTests
- 6. Spesifikasi Endpoint Lengkap
- error_envelope
- Proposal Bank sampah - Untuk Klien Pak Arfan.md
- PickupWorkflowTests
- 05 — Business Rules & SOPs
- ActivityListTests
- PenukaranPoinViewSet
- success_response
- NasabahDataIsolationTests
- price_history.py
- PemerintahReadOnlyTests
- MiruPagination
- RegistrationTests
- MIRU Backend Feature Testing
- DepositFlowTests
- PickupActionTests
- core/urls.py
- UserViewSet
- DepositCreateTests
- .partial_update
- 09 — Data Dictionary & Reference Values (Backend)
- Timeline Proyek Pengembangan MIRU Bank Sampah - Distrik Mimika Baru.md
- RedemptionApproveTests
- UserListFilterTests
- Detail Endpoint Backend per Modul
- OTP Development Mode (`OTP_DEV_FIXED_CODE`)
- pdf_receipt.py
- Detail Setiap Tabel
- Timeline Proyek Pengembangan Sistem Aplikasi Manajemen Peternakan-Klien Agung.md
- ⚠️ BATASAN KERAS — INI TIDAK BOLEH DIIMPLEMENTASIKAN
- settings_views.py
- Aturan Clean Code
- lan_proxy.py
- DashboardOverviewView
- Command
- PartnerSaleTests
- 01 — Project Overview: MIRU Bank Sampah (Miru-G)
- WasteCategoryAdminCrudTests
- Persyaratan yang harus disiapkan oleh klien.md
- main
- ComplaintManageTests
- RedemptionActionTests
- WithdrawalActionTests
- WithdrawalApproveTests
- WithdrawalCreateTests
- ValidationError
- device_token_views.py
- MediaUploadTests
- Backup & Recovery — MIRU Bank Sampah
- media_views.py
- run_all_tests.py
- ComplaintCreateTests
- Notifikasi
- RewardAdminCrudTests
- asgi.py
- wsgi.py
- UserProfileSerializer
- CookieAuthRequestTests
- DepositReadFilterTests
- Pengumuman
- api/urls.py
- logging_filters.py
- UserPatchPermissionTests
- seed_images.py
- KoordinatorAccessTests
- middleware.py
- require_complete_address
- 0020_penukaran_poin_snapshot_status.py
- MIRU Bank Sampah (Miru-G) — Ekosistem Aplikasi
- 0022_audit_t6_t7_t8.py
- 0026_pdp_minimise_identity.py
- Jawaban_Persyaratan_MIRU_Bank_Sampah.md
- 02 — Architecture & Tech Stack (Backend)
- verify_restored_api.py
- 0001_initial.py
- 0002_penjemputan_dalam_perjalanan.py
- WriteRateLimitTests
- 0003_pengaduan_fields.py
- 0004_user_role_pemerintah.py
- Selesai
- 0005_penarikan_ditolak.py
- 0006_auditlog.py
- RTK - Rust Token Killer
- MIRU Backend API — Agent Rules
- graphify
- public_object_url
- 0007_pengaturan_institusi.py
- 0008_riwayat_harga.py
- 0009_user_privacy_consent.py
- 0010_alter_kategorisampah_options_and_more.py
- serializers.py
- 0011_transfer_account_fields.py
- 0012_notifikasi.py
- 0013_konten_edukasi.py
- 0014_riwayat_harga_tanggal_berlaku.py
- 0015_wilayah_layanan.py
- 0016_fase8_4_identitas.py
- 0017_fase8_5_poin_expiry.py
- 0018_fase8_6_device_token_fcm.py
- 0019_penjemputan_lokasi.py
- CookieAuthLoginTests
- 0021_t2_phone_otp_verified.py
- 0023_kontenedukasi_gambar_url.py
- 0024_user_avatar_url.py
- 0025_institusi_tentang_kebijakan.py
- 0027_institusi_syarat_ketentuan.py
- 0028_alter_kontenedukasi_options.py
- 0029_alter_phoneotp_purpose.py
- DepositCorrectionTests
- MeEndpointTests
- filter_nasabah_owned
- test_cookie_auth.py
- UserAdminSerializer
- MitraPengepulCrudTests
- LoginRateLimitTests
- CookieOrHeaderJWTAuthentication
- CurrentRequestMiddleware
- pickups.py
- _create_audit_entry
- deposits.py
- _get_fernet
- IsPemerintahReadOnly
- models.py
- permissions.py
- exception_handler.py
- TransaksiSetoranViewSet
- PenukaranPoin

## God Nodes (most connected - your core abstractions)
1. `EnvelopeAPITestCase` - 106 edges
2. `success_response()` - 79 edges
3. `User` - 77 edges
4. `♻` - 76 edges
5. `KategoriSampah` - 57 edges
6. `TransaksiSetoran` - 44 edges
7. `PenarikanSaldo` - 44 edges
8. `Command` - 43 edges
9. `Penjemputan` - 37 edges
10. `Meta` - 36 edges

## Surprising Connections (you probably didn't know these)
- `MiruTokenObtainPairView` --uses--> `User`  [INFERRED]
  api/auth_views.py → api/models.py
- `MiruTokenObtainPairView` --uses--> `LoginAnonRateThrottle`  [INFERRED]
  api/auth_views.py → api/throttles.py
- `LoginRateLimitTests` --uses--> `MiruTokenObtainPairView`  [INFERRED]
  api/tests/test_rate_limiting.py → api/auth_views.py
- `ForgotPasswordView` --uses--> `User`  [INFERRED]
  api/auth_views.py → api/models.py
- `ForgotPasswordView` --uses--> `LoginAnonRateThrottle`  [INFERRED]
  api/auth_views.py → api/throttles.py

## Import Cycles
- None detected.

## Communities (166 total, 62 thin omitted)

### Community 0 - "Penjemputan"
Cohesion: 0.06
Nodes (53): Any, ApiConfig, Penjemputan, connect_notification_signals(), disconnect_notification_signals(), _nasabah_dijadwalkan_deskripsi(), _notif_penarikan(), _notif_pengaduan() (+45 more)

### Community 1 - "reports.py"
Cohesion: 0.15
Nodes (31): penarikan_total(), penukaran_count(), Shared aggregation helpers for dashboard and report endpoints., Total berat (kg) and nilai (Rp) grouped per kategori for a period., setoran_summary(), tonase_per_jenis(), get_deposit_chart(), day_bounds() (+23 more)

### Community 2 - "delete_account_views.py"
Cohesion: 0.16
Nodes (16): AnonRateThrottle, DeleteAccountCheckView, DeleteAccountConfirmView, DeleteAccountRequestOtpView, _get_nasabah_for_deletion(), APIView, extend_schema, Self-service hapus akun nasabah — kewajiban Play Store. Alur (konfirmasi… (+8 more)

### Community 3 - "11 — Security & Privacy (Backend — Sumber Kanonik)"
Cohesion: 0.07
Nodes (26): 10. Secrets & Supply Chain, 11. Integrasi Pihak Ketiga (Keamanan), 11 — Security & Privacy (Backend — Sumber Kanonik), 12. Checklist Go-Live Keamanan (Backend), 13. Mapping ke Dokumen Lain, 14. Aturan untuk AI / Engineer, 1. Prinsip Keamanan Ekosistem, 2. Klasifikasi Data (+18 more)

### Community 4 - "signals.py"
Cohesion: 0.17
Nodes (18): audit_post_delete(), audit_post_save(), audit_pre_save(), _capture_pre_save(), _get_changed_fields(), _get_pre_save_state(), _is_significant(), Signal handlers for automatic AuditLog recording. Uses pre_save to capture old… (+10 more)

### Community 6 - "PhoneOTP"
Cohesion: 0.06
Nodes (19): Command, BaseCommand, Management command: expire_poin Menghanguskan poin nasabah yang sudah melebihi…, AuditLog, Meta, PasswordResetToken, PhoneOTP, PoinTransaksi (+11 more)

### Community 8 - "User"
Cohesion: 0.17
Nodes (20): AbstractUser, User, approve_withdrawal(), _ensure_pending(), is_besar(), purge_lampiran_ktp(), Decimal, Business rules for saldo withdrawal requests. (+12 more)

### Community 9 - "EnvelopeAPITestCase"
Cohesion: 0.04
Nodes (18): EnvelopeAPITestCase, Set credential JWT langsung (bukan via endpoint login) agar: - Tidak kena…, Base test case with envelope helpers and user factories., AddressGateTests, AdminPhoneVerifiedTests, ForgotPasswordOtpTests, LoginTests, PhoneRequestOtpHijackTests (+10 more)

### Community 10 - "_backup_lib.sh"
Cohesion: 0.16
Nodes (23): miru_container_runtime(), miru_drop_database(), miru_ensure_database(), miru_find_db_container(), miru_gpg_decrypt(), miru_gpg_encrypt(), miru_load_env(), miru_pg_dump() (+15 more)

### Community 11 - "monitoring_views.py"
Cohesion: 0.14
Nodes (23): DetailSetoran, InventoryHistoryView, Monitoring endpoints: dashboard (Modul 15), laporan (Modul 16), inventory…, fmt(), Format a Decimal/number as a fixed 2-decimal string ('0.00' for None)., stok_per_kategori(), get_overview(), get_petugas_overview() (+15 more)

### Community 12 - "whatsapp.py"
Cohesion: 0.12
Nodes (23): create_and_send_otp(), generate_otp_code(), get_dev_fixed_otp(), _hash_otp(), invalidate_active_otps(), mask_phone(), normalize_phone(), otp_dev_mode_enabled() (+15 more)

### Community 13 - "ReportTestMixin"
Cohesion: 0.10
Nodes (6): DailyReportTests, EvaluationReportTests, MonthlyReportTests, ReportTestMixin, WasteReportTests, WeeklyReportTests

### Community 14 - "PengaturanInstitusi"
Cohesion: 0.08
Nodes (15): DeviceTokenAdmin, KontenEdukasiAdmin, NotifikasiAdmin, PasswordResetTokenAdmin, PengaturanInstitusiAdmin, PengumumanAdmin, PoinTransaksiAdmin, RiwayatHargaAdmin (+7 more)

### Community 16 - "openapi.py"
Cohesion: 0.11
Nodes (12): NotifikasiViewSet, action, ViewSet untuk notifikasi in-app. - Nasabah & petugas hanya melihat notifikasi…, Tandai satu notifikasi sebagai sudah dibaca., Tandai semua notifikasi milik user login sebagai sudah dibaca., _export_schema(), extend_schema, OpenAPI / drf-spectacular configuration helpers. (+4 more)

### Community 17 - "ledger.py"
Cohesion: 0.07
Nodes (45): PenjualanMitraCreateSerializer, adjust_setoran_correction(), complete_penukaran_poin(), create_setoran_with_side_effects(), credit_nasabah_setoran(), debit_nasabah_poin(), debit_nasabah_saldo(), decrease_kategori_stok() (+37 more)

### Community 18 - "ExportBaseView"
Cohesion: 0.13
Nodes (14): ExportBaseView, ExportDailyView, ExportEvaluationView, ExportMonthlyView, ExportWasteView, ExportWeeklyView, APIView, Base view for Excel export endpoints. (+6 more)

### Community 19 - "excel_export.py"
Cohesion: 0.22
Nodes (20): Views for exporting reports as .xlsx files (Fase 8.6). Each endpoint mirrors…, _auto_width(), export_daily(), export_evaluation(), export_monthly(), export_waste(), export_weekly(), Excel export service for MIRU reports (Modul 16). Generates .xlsx files for… (+12 more)

### Community 20 - "MonitorView"
Cohesion: 0.08
Nodes (18): DashboardDepositChartView, DashboardRecentActivityView, InventoryView, MonitorView, Base view for admin/koordinator/pemerintah read-only monitoring., ReportDailyView, ReportEvaluationView, ReportMonthlyView (+10 more)

### Community 21 - "DeleteAccountTests"
Cohesion: 0.20
Nodes (3): DeleteAccountTests, patch, `check` must not disclose nama/saldo/poin/riwayat before the caller proves…

### Community 22 - "KontenEdukasi"
Cohesion: 0.11
Nodes (9): KontenEdukasi, Konten edukasi sampah — artikel/panduan untuk nasabah (Modul 4)., EdukasiMarkdownTests, Konten edukasi — Markdown mentah (T8)., EdukasiGambarUrlTests, Unggah gambar edukasi + sajian /objects/ (filesystem fallback)., TestCase, SeedDataFullTests (+1 more)

### Community 23 - "PriceHistoryTests"
Cohesion: 0.13
Nodes (6): PriceHistoryTests, Regression: tanggal_berlaku ≥ H+3 (tepat 72 jam) masih diterima., Tanggal di masa lalu harus ditolak., Helper: return a datetime H+4 from now (past H+3 minimum)., If no tanggal_berlaku provided, default to H+3., H+1 should be rejected.

### Community 24 - "♻"
Cohesion: 0.03
Nodes (75): ♻, 10.1 Tujuan, 10.2 Alur Input Data, 10.3 Ketentuan, 10. SOP Input Data ke Aplikasi, 11.1 Tujuan, 11.2 Alur Penarikan Saldo, 11.3 Ketentuan (+67 more)

### Community 25 - "flow_docs_data.py"
Cohesion: 0.27
Nodes (7): _envelope(), get_demo_user(), get_nav_groups(), _meta(), Flow-based API documentation data for MIRU Bank Sampah., FlowDocsView, TemplateView

### Community 26 - "KontenEdukasiSerializer"
Cohesion: 0.17
Nodes (4): KontenEdukasiSerializer, CRUD konten edukasi — admin/koordinator., normalize_stored_media_ref(), Simpan key objek bila URL berasal dari /objects/; URL eksternal tetap utuh.

### Community 28 - "6. Spesifikasi Endpoint Lengkap"
Cohesion: 0.04
Nodes (48): 04 — API Contracts & Standards, 10. Mapping Role → Endpoint Access, 11. Catatan Implementasi, 1.1 Route Naming (English, kebab-case), 1. Prinsip Desain API, 2.1 Login, 2.2 Refresh Token, 2.3 Profil User Login (+40 more)

### Community 29 - "error_envelope"
Cohesion: 0.19
Nodes (12): clear_auth_cookies(), _validation_error(), Verifikasi OTP aktif; raise ValidationError jika gagal., verify_otp_code(), EnvelopeJSONRenderer, Wraps all DRF JSON responses in the standard MIRU envelope., build_meta(), error_envelope() (+4 more)

### Community 30 - "Proposal Bank sampah - Untuk Klien Pak Arfan.md"
Cohesion: 0.05
Nodes (39): **10.1 Mekanisme Revisi dan UAT**, **10. PRODUK DAN LAYANAN YANG DIDAPATKAN**, **11. PENUTUP**, **1.1 Pendahuluan**, **1.2 Tujuan**, **1.3 Cakupan Program dan Sistem**, **1. EXECUTIVE SUMMARY**, **2. PROFIL PERUSAHAAN** (+31 more)

### Community 31 - "PickupWorkflowTests"
Cohesion: 0.12
Nodes (3): PickupWorkflowTests, Tidak boleh disetujui tanpa petugas., Tab Aktif admin memakai ?status__in=disetujui,dijadwalkan,...

### Community 32 - "05 — Business Rules & SOPs"
Cohesion: 0.08
Nodes (24): 05 — Business Rules & SOPs, A.1 Konversi Setoran ke Saldo, A.2 Konversi Saldo ke Poin Reward, A.3 Penarikan Saldo, A.4 Penukaran Poin, A. Aturan Keuangan, B.1 Setor Langsung (di Kantor), B.2 Penjemputan (via Aplikasi) (+16 more)

### Community 34 - "PenukaranPoinViewSet"
Cohesion: 0.11
Nodes (10): NasabahLookupSerializer, PenarikanSaldoSerializer, PenukaranPoinSerializer, Data nasabah untuk petugas (scan QR / cari nasabah)., PenarikanSaldoViewSet, PenukaranPoinViewSet, action, atomic (+2 more)

### Community 35 - "success_response"
Cohesion: 0.10
Nodes (9): IsAdmin, success_response(), KategoriSampahViewSet, KontenEdukasiViewSet, RewardViewSet, WilayahLayananViewSet, edukasi_schema, reward_schema (+1 more)

### Community 36 - "NasabahDataIsolationTests"
Cohesion: 0.12
Nodes (7): NasabahDataIsolationTests, Nasabah hanya melihat penukaran poin milik sendiri., Nasabah hanya melihat notifikasi milik sendiri., Nasabah A cannot retrieve deposit milik nasabah B., Nasabah A cannot retrieve pickup milik nasabah B., Nasabah A cannot retrieve complaint milik nasabah B., Nasabah hanya melihat withdrawal milik sendiri.

### Community 37 - "price_history.py"
Cohesion: 0.17
Nodes (12): get_current_user(), Get the current user from thread-local storage., _auto_create_pengumuman(), get_active_price(), Decimal, Price change history for waste categories. Fase 8.2 — Kebijakan perubahan harga…, Get the currently active price for a category. Checks if there's a scheduled…, Validasi tanggal_berlaku minimal H+3 dari ref_time (default: now). (+4 more)

### Community 39 - "MiruPagination"
Cohesion: 0.18
Nodes (10): AuditLogSerializer, RiwayatHargaSerializer, get_price_history(), Return price history queryset for a category., MiruPagination, ActivityListView, AuditLogListView, APIView (+2 more)

### Community 41 - "MIRU Backend Feature Testing"
Cohesion: 0.14
Nodes (13): 1. Extend `EnvelopeAPITestCase`, 2. Assert JSON Envelope (required), 3. File Organization, 4. What to Test per Feature, 5. Use English Routes, 6. Seed Data for Manual / Integration Tests, Do Not, MIRU Backend Feature Testing (+5 more)

### Community 44 - "core/urls.py"
Cohesion: 0.13
Nodes (12): _cookie_kwargs(), MiruTokenObtainPairView, MiruTokenRefreshView, Set cookie HttpOnly untuk web admin (dipakai bersamaan dengan body JSON…, set_auth_cookies(), HealthCheckView, APIView, auth_login_schema (+4 more)

### Community 45 - "UserViewSet"
Cohesion: 0.18
Nodes (6): IsStaffManagerOrPetugas, IsUserOwnerOrAdmin, Object-level permission for the User model (/api/users/{id}/)., Admin, koordinator, atau petugas — untuk lookup nasabah., UserViewSet, user_viewset_schema

### Community 47 - ".partial_update"
Cohesion: 0.18
Nodes (3): PengaduanSerializer, PengaduanViewSet, complaint_schema

### Community 48 - "09 — Data Dictionary & Reference Values (Backend)"
Cohesion: 0.08
Nodes (23): 09 — Data Dictionary & Reference Values (Backend), A.1 Daftar Jenis Sampah yang Diterima, A.2 Ketentuan Kategori, A. KATEGORI & HARGA SAMPAH (Seed Data), B. KATALOG REWARD (Seed Data), C.1 Konversi Setoran, C.2 Contoh Perhitungan (dari SOP), C.3 Aturan Keuangan Ringkas (+15 more)

### Community 49 - "Timeline Proyek Pengembangan MIRU Bank Sampah - Distrik Mimika Baru.md"
Cohesion: 0.10
Nodes (20): **1. INFORMASI PROYEK**, **2. KETENTUAN UMUM TIMELINE**, **3. RINGKASAN CAKUPAN MODUL (17 MODUL SISTEM)**, **4. DETAIL TIMELINE PROYEK**, **5. KETENTUAN KHUSUS IMPLEMENTASI**, **6. KETENTUAN PERUBAHAN TIMELINE**, **7. PENUTUP**, **DISTRIK MIMIKA BARU, KABUPATEN MIMIKA, PAPUA TENGAH** (+12 more)

### Community 51 - "UserListFilterTests"
Cohesion: 0.11
Nodes (3): AdminCreateStaffTests, UserListFilterTests, UserResponseSecurityTests

### Community 52 - "Detail Endpoint Backend per Modul"
Cohesion: 0.10
Nodes (19): 07 — Modules & Features (Backend), 17 Modul Sistem — Peran Backend, Detail Endpoint Backend per Modul, Modul 10: Penarikan Saldo, Modul 11: Poin & Reward, Modul 12: Stok Gudang, Modul 13: Penjualan ke Mitra, Modul 14: Pengaduan (+11 more)

### Community 53 - "OTP Development Mode (`OTP_DEV_FIXED_CODE`)"
Cohesion: 0.06
Nodes (30): Alternatif cepat tanpa OTP tetap, Cara aktifkan, Endpoint yang terpengaruh, Kaitan proposal / modul, Masalah yang diselesaikan, OTP Development Mode (`OTP_DEV_FIXED_CODE`), Production / staging dengan WA nyata, Syarat keamanan (wajib) (+22 more)

### Community 54 - "pdf_receipt.py"
Cohesion: 0.16
Nodes (13): DownloadDepositReceiptView, DownloadWithdrawalReceiptView, APIView, Download PDF bukti setoran. Role-gated: - Nasabah → hanya unduh milik sendiri -…, Download PDF tanda terima penarikan. Role-gated: - Nasabah → hanya unduh milik…, _format_rupiah(), generate_deposit_receipt(), generate_withdrawal_receipt() (+5 more)

### Community 55 - "Detail Setiap Tabel"
Cohesion: 0.12
Nodes (15): 03 — Database Schema & ERD (Backend Django), 10. PenjualanMitra, 11. Pengaduan, 1. User (extends AbstractUser), 2. KategoriSampah, 3. TransaksiSetoran, 4. DetailSetoran, 5. Penjemputan (+7 more)

### Community 56 - "Timeline Proyek Pengembangan Sistem Aplikasi Manajemen Peternakan-Klien Agung.md"
Cohesion: 0.12
Nodes (15): **1. INFORMASI PROYEK**, **2. KETENTUAN UMUM TIMELINE**, **3. DETAIL TIMELINE PROYEK**, **4. KETENTUAN KHUSUS IMPLEMENTASI**, **5. KETENTUAN PERUBAHAN TIMELINE**, **6. PENUTUP**, Catatan:, Catatan: (+7 more)

### Community 57 - "⚠️ BATASAN KERAS — INI TIDAK BOLEH DIIMPLEMENTASIKAN"
Cohesion: 0.12
Nodes (15): 06 — System Constraints (Batasan Sistem), 10. Publikasi Aplikasi, 11. Batasan Role, 12. Batasan Teknis Backend, 13. Keamanan & Privasi (dokumen khusus), 1. TIDAK ADA Integrasi Payment Gateway Otomatis, 2. TIDAK ADA GPS Live Tracking, 3. TIDAK ADA Integrasi Hardware Fisik (+7 more)

### Community 58 - "settings_views.py"
Cohesion: 0.06
Nodes (18): PengaturanInstitusiSerializer, PengumumanSerializer, Profil institusi. logo_url read-only (diabaikan pada write)., get_privacy_policy(), get_terms_of_service(), get_institution_settings(), Return the singleton institution settings row (creates defaults if missing)., InstitutionSettingsView (+10 more)

### Community 59 - "Aturan Clean Code"
Cohesion: 0.14
Nodes (13): 00 — System Prompt & Clean Code Rules, 10. Documentation, 1. Struktur & Organisasi, 2. Models (Django ORM), 3. Serializers, 4. Views & ViewSets, 5. Permissions, 6. Error Handling (+5 more)

### Community 60 - "lan_proxy.py"
Cohesion: 0.80
Nodes (4): handle(), main(), pipe(), socket

### Community 61 - "DashboardOverviewView"
Cohesion: 0.29
Nodes (6): DashboardOverviewView, APIView, Overview admin penuh, atau widget petugas (jemput hari ini / antrian aktif)., IsDashboardOverviewReader, Admin/koordinator/pemerintah (full) atau petugas (widget sendiri)., dashboard_overview_schema

### Community 62 - "Command"
Cohesion: 0.14
Nodes (4): Command, BaseCommand, Seed data wilayah layanan dari data dictionary §K., Create rich history for nasabah001 (Budi Santoso) and nasabah002 (Siti…

### Community 64 - "01 — Project Overview: MIRU Bank Sampah (Miru-G)"
Cohesion: 0.15
Nodes (12): 01 — Project Overview: MIRU Bank Sampah (Miru-G), 3 Repositori Sistem, 6 Role Pengguna, Indikator Keberhasilan Program, Informasi Aplikasi, Informasi Kontak & Organisasi, Jam Layanan Operasional, Latar Belakang (+4 more)

### Community 66 - "Persyaratan yang harus disiapkan oleh klien.md"
Cohesion: 0.17
Nodes (11): **6.1 Persyaratan Administratif Program**, **6.2 Persyaratan Data Operasional**, **6.3 Persyaratan Legalitas dan Kebijakan Internal**, **6.4 Persyaratan Akun Developer dan Publikasi Aplikasi**, **6.5 Persyaratan Infrastruktur dan Domain**, **6.6 Persyaratan Integrasi Pihak Ketiga**, **6.7 Persyaratan Perangkat Pendukung Operasional**, **6. PERSYARATAN DAN PERIZINAN YANG DISEDIAKAN KLIEN** (+3 more)

### Community 73 - "ValidationError"
Cohesion: 0.13
Nodes (17): PenjemputanCreateSerializer, atomic, get_activity_items(), _penarikan_items(), _penukaran_items(), Merged transaction history for nasabah activity feed., _resolve_nasabah_filter(), _setoran_items() (+9 more)

### Community 74 - "device_token_views.py"
Cohesion: 0.20
Nodes (8): DeviceTokenViewSet, extend_schema_view, Device token (FCM) registration endpoints — Fase 8.6., Register / unregister FCM device tokens. - POST /api/device-tokens/ { "token":…, DELETE by token string (body) — praktis dari mobile logout., DeviceTokenSerializer, error_response(), Response

### Community 75 - "MediaUploadTests"
Cohesion: 0.13
Nodes (5): AvatarUrlTests, MediaUploadTests, PDP: KTP hanya lampiran sementara penarikan ≥ 1 juta., WithdrawalKtpLampiranTests, SimpleUploadedFile

### Community 76 - "Backup & Recovery — MIRU Bank Sampah"
Cohesion: 0.06
Nodes (31): 1. Strategi Backup, 2. Jadwal & Retensi, 3. Lokasi Penyimpanan, 4. Prasyarat, 5. Cara Setup Cron, 6.1 Restore Terjadwal (dari file backup), 6.2 Restore Darurat (ketika aplikasi tidak bisa jalan), 6.3 Restore di Server Baru (migrasi) (+23 more)

### Community 77 - "media_views.py"
Cohesion: 0.12
Nodes (22): PublicObjectView, Unggah & sajikan objek publik (gambar edukasi)., GET /objects/<key> — gambar edukasi publik (tanpa auth)., clear_public_prefixes(), ensure_bucket(), _is_allowed_image_header(), ObjectNotFound, open_public_object() (+14 more)

### Community 80 - "Notifikasi"
Cohesion: 0.11
Nodes (5): Notifikasi, In-app notification untuk user nasabah., NotificationMarkReadTests, Tests for in-app notification mark-as-read endpoints., RedemptionCreateTests

### Community 84 - "UserProfileSerializer"
Cohesion: 0.15
Nodes (7): MeView, MiruTokenObtainPairSerializer, extend_schema_view, user_auth_payload(), UserProfileSerializer, serialized_media_url(), TokenObtainPairSerializer

### Community 85 - "CookieAuthRequestTests"
Cohesion: 0.09
Nodes (8): CookieAuthLogoutTests, CookieAuthMobileLogoutTests, CookieAuthRefreshTests, CookieAuthRequestTests, Access token sudah basi, tapi csrf cookie masih ada → logout tetap berhasil dan…, Klien mobile logout via Bearer header (access valid) + refresh di body — tanpa…, Buat user + pasang cookie access/refresh/csrf seolah-olah baru login., Setelah login (cookie tersimpan otomatis di test client), request berikutnya…

### Community 87 - "Pengumuman"
Cohesion: 0.13
Nodes (6): DeviceToken, Pengumuman, FCM device token milik user (Fase 8.6)., DeviceTokenAPITests, FcmTriggerTests, Tests for FCM device tokens and safe payloads (Fase 8.6).

### Community 88 - "api/urls.py"
Cohesion: 0.34
Nodes (12): ForgotPasswordView, LogoutView, PhoneRequestOtpView, PhoneVerifyOtpView, PoinInfoView, APIView, extend_schema, ResetPasswordRequestOtpView (+4 more)

### Community 89 - "logging_filters.py"
Cohesion: 0.22
Nodes (8): JSONFormatter, PIIRedactFilter, Logging filters untuk MIRU Bank Sampah. Fungsi: - Redact PII (password, token,…, Redact all sensitive data from a log string., Logging filter yang meredact PII dari log messages. Gunakan di…, JSON log formatter untuk structured logging. Output: satu baris JSON per log…, redact_sensitive(), LogRecord

### Community 91 - "seed_images.py"
Cohesion: 0.29
Nodes (10): _color_index(), _font(), _initials(), Gambar demo untuk seed — generate PNG, upload via object_storage (jadi WebP)., reset_seed_image_cache(), _to_upload(), upload_article_cover(), upload_avatar() (+2 more)

### Community 93 - "middleware.py"
Cohesion: 0.22
Nodes (5): get_client_ip(), Extract client IP from request headers., Middleware untuk mencatat setiap request dalam format JSON. - Mencatat method,…, RequestIdMiddleware, RequestLoggingMiddleware

### Community 94 - "require_complete_address"
Cohesion: 0.25
Nodes (6): PenukaranPoinCreateSerializer, has_complete_address(), Helpers profil nasabah — kelengkapan alamat untuk gate transaksi (T2)., Alamat teks wajib. Koordinat/wilayah opsional sampai Maps penuh., Blok transaksi jika alamat profil belum diisi. action_label contoh: 'mengajukan…, require_complete_address()

### Community 96 - "MIRU Bank Sampah (Miru-G) — Ekosistem Aplikasi"
Cohesion: 0.20
Nodes (9): 6 Role Pengguna, Arsitektur Sistem, Kontak & Instansi, MIRU Bank Sampah (Miru-G) — Ekosistem Aplikasi, Quick Start (Development Lokal), Referensi API Live (saat backend berjalan), Repositori GitHub, Standarisasi Lintas Repositori (+1 more)

### Community 99 - "Jawaban_Persyaratan_MIRU_Bank_Sampah.md"
Cohesion: 0.22
Nodes (8): **6.1 Persyaratan Administratif Program**, **6.2 Persyaratan Data Operasional**, **6.3 Persyaratan Legalitas dan Kebijakan Internal**, **6.4 Persyaratan Akun Developer dan Publikasi Aplikasi**, **6.5 Persyaratan Infrastruktur dan Domain**, **6.6 Persyaratan Integrasi Pihak Ketiga**, **6.7 Persyaratan Perangkat Pendukung Operasional**, **JAWABAN PERSYARATAN KLIEN**

### Community 100 - "02 — Architecture & Tech Stack (Backend)"
Cohesion: 0.25
Nodes (7): 02 — Architecture & Tech Stack (Backend), API Documentation, Arsitektur, CORS Configuration, Environment Variables (`.env`), Struktur Folder, Tech Stack

### Community 104 - "WriteRateLimitTests"
Cohesion: 0.19
Nodes (8): POST requests kena throttle write., Verifikasi write throttle class terpasang secara global., Scope write memiliki rate 100/hour., GET requests tidak kena throttle write., WriteRateLimitTests, 100 requests per hour untuk write operations per user. GET/HEAD/OPTIONS tidak…, WriteUserRateThrottle, UserRateThrottle

### Community 107 - "Selesai"
Cohesion: 0.11
Nodes (18): 08 — Task List: Backend, Bisa langsung, Bisa langsung, Fase 0 — Foundation, Fase 1 — Auth & envelope, Fase 2 — Bisnis inti, Fase 3 — Operasional, Fase 4 — Monitoring & laporan (+10 more)

### Community 110 - "RTK - Rust Token Killer"
Cohesion: 0.33
Nodes (5): graphify, Hook-Based Usage, Installation Verification, Meta Commands (always use rtk directly), RTK - Rust Token Killer

### Community 111 - "MIRU Backend API — Agent Rules"
Cohesion: 0.40
Nodes (4): Graphify Knowledge Graph, MIRU Backend API — Agent Rules, Stack, Token Savers (WAJIB)

### Community 112 - "graphify"
Cohesion: 0.40
Nodes (4): ⚠️ AI Steering — baca on-demand (jangan semua sekaligus), Aturan Keras, graphify, MIRU Bank Sampah — Backend API (Django)

### Community 113 - "public_object_url"
Cohesion: 0.29
Nodes (6): MediaUploadView, APIView, extend_schema, MediaUploadSerializer, public_object_url(), Request

### Community 118 - "serializers.py"
Cohesion: 0.06
Nodes (21): DetailSetoranReadSerializer, DetailSetoranSerializer, DetailSetoranWriteSerializer, KategoriSampahSerializer, KontenEdukasiPublicSerializer, Meta, MitraPengepulSerializer, PenarikanSaldoCreateSerializer (+13 more)

### Community 128 - "CookieAuthLoginTests"
Cohesion: 0.25
Nodes (4): CookieAuthLoginTests, override_settings, Login harus mengembalikan token di body (kompatibilitas mobile) DAN men-set…, Cookie access_token basi/tidak valid yang masih nempel di browser tidak boleh…

### Community 148 - "filter_nasabah_owned"
Cohesion: 0.20
Nodes (6): filter_nasabah_owned(), filter_pickup_queryset(), filter_staff_only(), Reusable queryset filters per role., Admin/koordinator/pemerintah read; others denied., Nasabah sees own data; staff roles see all; petugas sees own operational rows.

### Community 149 - "test_cookie_auth.py"
Cohesion: 0.33
Nodes (4): CookieAuthMobileHeaderUnaffectedTests, CookieAuthTestCase, Klien mobile (header Authorization, tanpa cookie sama sekali) tidak boleh…, Base cookie-auth test. Sebagian besar pengujian memakai cookie yang di-seed…

### Community 152 - "LoginRateLimitTests"
Cohesion: 0.33
Nodes (4): LoginRateLimitTests, Verifikasi throttle class terpasang di endpoint login., MiruTokenObtainPairView memiliki throttle_classes., Login throttle mechanism berjalan tanpa error (tidak 500).

### Community 153 - "CookieOrHeaderJWTAuthentication"
Cohesion: 0.50
Nodes (3): CookieOrHeaderJWTAuthentication, Header hadir → perilaku identik dengan `JWTAuthentication` bawaan (dipakai…, JWTAuthentication

### Community 155 - "pickups.py"
Cohesion: 0.07
Nodes (30): Meta, PenjemputanFilter, Supports ?status=menunggu and ?status__in=disetujui,dijadwalkan,..., PenjemputanSerializer, PenjemputanUpdateSerializer, PickupApproveSerializer, PickupAssignSerializer, PickupStatusActionSerializer (+22 more)

### Community 156 - "_create_audit_entry"
Cohesion: 0.50
Nodes (4): get_current_request(), Access the current request from thread-local storage (for signals etc.)., _create_audit_entry(), Create an AuditLog entry from the current request context.

### Community 171 - "deposits.py"
Cohesion: 0.13
Nodes (14): TransaksiSetoranCreateSerializer, build_bukti_digital(), build_detail_data(), _coerce_positive_int(), parse_nasabah_lookup_query(), prepare_details_data(), Decimal, Business rules and price calculation for deposit transactions. (+6 more)

### Community 172 - "_get_fernet"
Cohesion: 0.28
Nodes (8): decrypt_value(), encrypt_value(), _get_fernet(), Field-level encryption service for sensitive data (NIK, KTP data at-rest). Uses…, Derive a 32-byte URL-safe base64 key from Django's SECRET_KEY. This ensures…, Encrypt a plaintext string. Returns a base64-encoded ciphertext string., Decrypt a ciphertext string back to plaintext., Fernet

### Community 174 - "IsPemerintahReadOnly"
Cohesion: 0.21
Nodes (5): IsNasabah, IsOwnerOrAdmin, IsPemerintahReadOnly, IsPickupManager, Pemerintah distrik: hanya boleh akses read (GET/HEAD/OPTIONS).

### Community 188 - "models.py"
Cohesion: 0.17
Nodes (13): CharInFilter, TransaksiSetoranFilter, KategoriSampah, MitraPengepul, PenarikanSaldo, Pengaduan, PenjualanMitra, Reward (+5 more)

### Community 197 - "permissions.py"
Cohesion: 0.11
Nodes (12): _client_ip(), DownloadLampiranKTPView, Views for downloading KTP lampiran (pending only) and PDF receipts (role-gated)., Unduh lampiran KTP penarikan besar — hanya selama status menunggu. Setelah…, IsAdminOrKoordinator, IsMonitorReadOnly, Admin, koordinator, pemerintah — akses read untuk monitoring., PenjualanMitraSerializer (+4 more)

### Community 199 - "exception_handler.py"
Cohesion: 0.39
Nodes (7): Rate limit login mengembalikan pesan BI + sisa detik, bukan teks Inggris., _flatten_errors(), _get_error_code(), _get_error_message(), miru_exception_handler(), _throttle_wait_seconds(), Throttled

### Community 202 - "TransaksiSetoranViewSet"
Cohesion: 0.19
Nodes (4): IsPetugasOrAdmin, TransaksiSetoranReadSerializer, TransaksiSetoranViewSet, deposit_schema

### Community 208 - "PenukaranPoin"
Cohesion: 0.15
Nodes (18): AlreadyProcessedError, InvalidStatusTransitionError, PenukaranPoin, PenarikanSaldoUpdateSerializer, PenukaranPoinUpdateSerializer, approve_redemption(), cancel_redemption(), _ensure_pending() (+10 more)

## Knowledge Gaps
- **461 isolated node(s):** `CharInFilter`, `Migration`, `Migration`, `Migration`, `Migration` (+456 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1260 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **62 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EnvelopeAPITestCase` connect `EnvelopeAPITestCase` to `Penjemputan`, `PhoneOTP`, `InventoryHistoryTests`, `whatsapp.py`, `ReportTestMixin`, `DepositCorrectionTests`, `MeEndpointTests`, `test_cookie_auth.py`, `DeleteAccountTests`, `KontenEdukasi`, `MitraPengepulCrudTests`, `PriceHistoryTests`, `LoginRateLimitTests`, `DashboardOverviewTests`, `PickupWorkflowTests`, `ActivityListTests`, `NasabahDataIsolationTests`, `PemerintahReadOnlyTests`, `RegistrationTests`, `DepositFlowTests`, `PickupActionTests`, `DepositCreateTests`, `RedemptionApproveTests`, `UserListFilterTests`, `settings_views.py`, `models.py`, `PartnerSaleTests`, `WasteCategoryAdminCrudTests`, `ComplaintManageTests`, `RedemptionActionTests`, `WithdrawalActionTests`, `WithdrawalApproveTests`, `WithdrawalCreateTests`, `MediaUploadTests`, `ComplaintCreateTests`, `Notifikasi`, `RewardAdminCrudTests`, `DepositReadFilterTests`, `Pengumuman`, `UserPatchPermissionTests`, `KoordinatorAccessTests`, `WriteRateLimitTests`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Why does `KategoriSampah` connect `models.py` to `reports.py`, `signals.py`, `PhoneOTP`, `InventoryHistoryTests`, `EnvelopeAPITestCase`, `monitoring_views.py`, `ReportTestMixin`, `ledger.py`, `DepositCorrectionTests`, `KontenEdukasi`, `PriceHistoryTests`, `ActivityListTests`, `NasabahDataIsolationTests`, `price_history.py`, `PemerintahReadOnlyTests`, `DepositFlowTests`, `deposits.py`, `DepositCreateTests`, `Command`, `PartnerSaleTests`, `WasteCategoryAdminCrudTests`, `DepositReadFilterTests`, `KoordinatorAccessTests`, `WriteRateLimitTests`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `success_response()` connect `success_response` to `PenukaranPoinViewSet`, `permissions.py`, `User`, `device_token_views.py`, `monitoring_views.py`, `core/urls.py`, `media_views.py`, `TransaksiSetoranViewSet`, `.partial_update`, `openapi.py`, `public_object_url`, `UserViewSet`, `UserProfileSerializer`, `MonitorView`, `api/urls.py`, `settings_views.py`, `pickups.py`, `error_envelope`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 54 inferred relationships involving `User` (e.g. with `ForgotPasswordView` and `MiruTokenObtainPairView`) actually correct?**
  _`User` has 54 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `KategoriSampah` (e.g. with `Command` and `stok_per_kategori()`) actually correct?**
  _`KategoriSampah` has 34 INFERRED edges - model-reasoned connections that need verification._
- **What connects `CharInFilter`, `Migration`, `Migration` to the rest of the system?**
  _461 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Penjemputan` be split into smaller, more focused modules?**
  _Cohesion score 0.05913461538461538 - nodes in this community are weakly interconnected._