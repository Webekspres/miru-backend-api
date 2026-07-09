from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .settings_views import InstitutionSettingsView, PengumumanListView, PrivacyPolicyView
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

urlpatterns = [
    path('activity/', ActivityListView.as_view(), name='activity'),
    path('audit-log/', AuditLogListView.as_view(), name='audit-log'),
    path('settings/', InstitutionSettingsView.as_view(), name='settings'),
    path('pengumuman/', PengumumanListView.as_view(), name='pengumuman'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
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
    path('', include(router.urls)),
]
