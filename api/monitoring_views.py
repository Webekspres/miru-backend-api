"""Monitoring endpoints: dashboard (Modul 15), laporan (Modul 16), inventory (Modul 12)."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .openapi import (
    dashboard_deposit_chart_schema,
    dashboard_overview_schema,
    dashboard_recent_activity_schema,
    inventory_schema,
    inventory_history_schema,
    report_daily_schema,
    report_evaluation_schema,
    report_monthly_schema,
    report_weekly_schema,
    report_waste_schema,
)
from .permissions import IsDashboardOverviewReader, IsMonitorReadOnly
from .services.dashboard import (
    get_deposit_chart,
    get_overview,
    get_petugas_overview,
    get_recent_activity,
)
from .services.inventory import get_inventory_history, get_inventory_summary
from .services.reports import (
    daily_report,
    evaluation_report,
    monthly_report,
    waste_report,
    weekly_report,
)
from .utils.response import success_response


class MonitorView(APIView):
    """Base view for admin/koordinator/pemerintah read-only monitoring."""

    permission_classes = [IsAuthenticated, IsMonitorReadOnly]


@dashboard_overview_schema
class DashboardOverviewView(APIView):
    """Overview admin penuh, atau widget petugas (jemput hari ini / antrian aktif)."""

    permission_classes = [IsAuthenticated, IsDashboardOverviewReader]

    def get(self, request):
        if request.user.role == 'petugas':
            data = get_petugas_overview(request.user)
            message = 'Ringkasan dashboard petugas berhasil diambil.'
        else:
            data = get_overview()
            message = 'Ringkasan dashboard berhasil diambil.'
        return success_response(data=data, message=message, request=request)


@dashboard_deposit_chart_schema
class DashboardDepositChartView(MonitorView):
    def get(self, request):
        data = get_deposit_chart(
            request.query_params.get('bulan'),
            request.query_params.get('tahun'),
        )
        return success_response(
            data=data,
            message='Data chart setoran berhasil diambil.',
            request=request,
        )


@dashboard_recent_activity_schema
class DashboardRecentActivityView(MonitorView):
    def get(self, request):
        data = get_recent_activity(request.query_params.get('limit'))
        return success_response(
            data=data,
            message='Aktivitas terbaru berhasil diambil.',
            request=request,
        )


@report_daily_schema
class ReportDailyView(MonitorView):
    def get(self, request):
        return success_response(
            data=daily_report(request.query_params.get('tanggal')),
            message='Laporan harian berhasil diambil.',
            request=request,
        )


@report_weekly_schema
class ReportWeeklyView(MonitorView):
    def get(self, request):
        data = weekly_report(
            request.query_params.get('minggu'),
            request.query_params.get('tahun'),
        )
        return success_response(
            data=data,
            message='Laporan mingguan berhasil diambil.',
            request=request,
        )


@report_monthly_schema
class ReportMonthlyView(MonitorView):
    def get(self, request):
        data = monthly_report(
            request.query_params.get('bulan'),
            request.query_params.get('tahun'),
        )
        return success_response(
            data=data,
            message='Laporan bulanan berhasil diambil.',
            request=request,
        )


@report_waste_schema
class ReportWasteView(MonitorView):
    def get(self, request):
        data = waste_report(
            request.query_params.get('start'),
            request.query_params.get('end'),
        )
        return success_response(
            data=data,
            message='Laporan sampah berhasil diambil.',
            request=request,
        )


@report_evaluation_schema
class ReportEvaluationView(MonitorView):
    def get(self, request):
        data = evaluation_report(
            request.query_params.get('start'),
            request.query_params.get('end'),
        )
        return success_response(
            data=data,
            message='Data evaluasi berhasil diambil.',
            request=request,
        )


@inventory_schema
class InventoryView(MonitorView):
    def get(self, request):
        return success_response(
            data=get_inventory_summary(),
            message='Ringkasan stok berhasil diambil.',
            request=request,
        )


@inventory_history_schema
class InventoryHistoryView(MonitorView):
    def get(self, request, kategori_id):
        return success_response(
            data=get_inventory_history(kategori_id, request.query_params.get('limit')),
            message='Riwayat stok berhasil diambil.',
            request=request,
        )
