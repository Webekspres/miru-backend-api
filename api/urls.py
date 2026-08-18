from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .auth_views import (
    ForgotPasswordView,
    PhoneRequestOtpView,
    PhoneVerifyOtpView,
    PoinInfoView,
    ResetPasswordRequestOtpView,
    ResetPasswordVerifyOtpView,
    ResetPasswordView,
)
from .media_views import MediaUploadView
from .download_views import (
    DownloadDepositReceiptView,
    DownloadLampiranKTPView,
    DownloadWithdrawalReceiptView,
)
from .export_views import (
    ExportDailyView,
    ExportEvaluationView,
    ExportMonthlyView,
    ExportWasteView,
    ExportWeeklyView,
)
from .notifications_views import NotifikasiViewSet
from .device_token_views import DeviceTokenViewSet
from .settings_views import (
    InstitutionSettingsView,
    PengumumanListView,
    PrivacyPolicyView,
    TermsView,
)
from .delete_account_views import (
    DeleteAccountCheckView,
    DeleteAccountConfirmView,
    DeleteAccountRequestOtpView,
)
from .monitoring_views import (
    DashboardDepositChartView,
    DashboardOverviewView,
    DashboardRecentActivityView,
    InventoryView,
    InventoryHistoryView,
    ReportDailyView,
    ReportEvaluationView,
    ReportMonthlyView,
    ReportWasteView,
    ReportWeeklyView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'waste-categories', KategoriSampahViewSet, basename='waste-category')
router.register(r'deposits', TransaksiSetoranViewSet, basename='deposit')
router.register(r'pickups', PenjemputanViewSet, basename='pickup')
router.register(r'withdrawals', PenarikanSaldoViewSet, basename='withdrawal')
router.register(r'rewards', RewardViewSet, basename='reward')
router.register(r'reward-redemptions', PenukaranPoinViewSet, basename='reward-redemption')
router.register(r'partners', MitraPengepulViewSet, basename='partner')
router.register(r'partner-sales', PenjualanMitraViewSet, basename='partner-sale')
router.register(r'complaints', PengaduanViewSet, basename='complaint')
router.register(r'edukasi', KontenEdukasiViewSet, basename='edukasi')
router.register(r'wilayah', WilayahLayananViewSet, basename='wilayah')
router.register(r'notifications', NotifikasiViewSet, basename='notification')
router.register(r'device-tokens', DeviceTokenViewSet, basename='device-token')

urlpatterns = [
    path('media/uploads/', MediaUploadView.as_view(), name='media-upload'),
    path('activity/', ActivityListView.as_view(), name='activity'),
    path('audit-log/', AuditLogListView.as_view(), name='audit-log'),
    path('settings/', InstitutionSettingsView.as_view(), name='settings'),
    path('pengumuman/', PengumumanListView.as_view(), name='pengumuman'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('terms/', TermsView.as_view(), name='terms'),
    path(
        'device-tokens/unregister/',
        DeviceTokenViewSet.as_view({'delete': 'unregister'}),
        name='device-token-unregister',
    ),
    path('dashboard/overview/', DashboardOverviewView.as_view(), name='dashboard-overview'),
    path('dashboard/deposit-chart/', DashboardDepositChartView.as_view(), name='dashboard-deposit-chart'),
    path('dashboard/recent-activity/', DashboardRecentActivityView.as_view(), name='dashboard-recent-activity'),
    path('reports/daily/', ReportDailyView.as_view(), name='report-daily'),
    path('reports/weekly/', ReportWeeklyView.as_view(), name='report-weekly'),
    path('reports/monthly/', ReportMonthlyView.as_view(), name='report-monthly'),
    path('reports/waste/', ReportWasteView.as_view(), name='report-waste'),
    path('reports/evaluation/', ReportEvaluationView.as_view(), name='report-evaluation'),
    path('inventory/', InventoryView.as_view(), name='inventory'),
    path(
        'inventory/<int:kategori_id>/history/',
        InventoryHistoryView.as_view(),
        name='inventory-history',
    ),
    # T2 — Password reset OTP WA + verifikasi HP
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path(
        'auth/reset-password/request-otp/',
        ResetPasswordRequestOtpView.as_view(),
        name='reset-password-request-otp',
    ),
    path(
        'auth/reset-password/verify-otp/',
        ResetPasswordVerifyOtpView.as_view(),
        name='reset-password-verify-otp',
    ),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('auth/phone/request-otp/', PhoneRequestOtpView.as_view(), name='phone-request-otp'),
    path('auth/phone/verify-otp/', PhoneVerifyOtpView.as_view(), name='phone-verify-otp'),

    # Play Store — self-service hapus akun (konfirmasi mendalam + OTP WA)
    path(
        'auth/delete-account/check/',
        DeleteAccountCheckView.as_view(),
        name='delete-account-check',
    ),
    path(
        'auth/delete-account/request-otp/',
        DeleteAccountRequestOtpView.as_view(),
        name='delete-account-request-otp',
    ),
    path(
        'auth/delete-account/confirm/',
        DeleteAccountConfirmView.as_view(),
        name='delete-account-confirm',
    ),

    # Fase 8.5 — Info poin & masa berlaku
    path('auth/poin-info/', PoinInfoView.as_view(), name='poin-info'),

    # Fase 8.4 — PDF receipts (role-gated)
    path(
        'deposits/<int:deposit_id>/receipt/',
        DownloadDepositReceiptView.as_view(),
        name='deposit-receipt',
    ),
    path(
        'withdrawals/<int:withdrawal_id>/receipt/',
        DownloadWithdrawalReceiptView.as_view(),
        name='withdrawal-receipt',
    ),

    # Lampiran KTP penarikan besar — hanya admin/koordinator, hanya status menunggu
    path(
        'withdrawals/<int:withdrawal_id>/lampiran-ktp/',
        DownloadLampiranKTPView.as_view(),
        name='download-lampiran-ktp',
    ),

    # Fase 8.6 — Excel exports
    path('reports/daily/export/', ExportDailyView.as_view(), name='export-daily'),
    path('reports/weekly/export/', ExportWeeklyView.as_view(), name='export-weekly'),
    path('reports/monthly/export/', ExportMonthlyView.as_view(), name='export-monthly'),
    path('reports/waste/export/', ExportWasteView.as_view(), name='export-waste'),
    path('reports/evaluation/export/', ExportEvaluationView.as_view(), name='export-evaluation'),

    path('', include(router.urls)),
]
