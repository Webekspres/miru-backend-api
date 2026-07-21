"""
Views for exporting reports as .xlsx files (Fase 8.6).

Each endpoint mirrors the JSON report endpoint but returns an Excel file
instead. Role-gated: admin/koordinator/pemerintah only (IsMonitorReadOnly).
"""

from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .openapi import (
    export_daily_schema,
    export_evaluation_schema,
    export_monthly_schema,
    export_waste_schema,
    export_weekly_schema,
)
from .permissions import IsMonitorReadOnly
from .services.excel_export import (
    export_daily,
    export_evaluation,
    export_monthly,
    export_waste,
    export_weekly,
)


class ExportBaseView(APIView):
    """Base view for Excel export endpoints."""
    permission_classes = [IsAuthenticated, IsMonitorReadOnly]
    filename_prefix = 'laporan'
    filename_suffix = 'xlsx'

    def _excel_response(self, data: bytes, filename: str) -> HttpResponse:
        return HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}.xlsx"',
                'Content-Length': str(len(data)),
            },
        )


@export_daily_schema
class ExportDailyView(ExportBaseView):
    filename_prefix = 'laporan_harian'

    def get(self, request):
        tanggal = request.query_params.get('tanggal')
        data = export_daily(tanggal)
        filename = f'{self.filename_prefix}_{tanggal or "hari_ini"}'
        return self._excel_response(data, filename)


@export_weekly_schema
class ExportWeeklyView(ExportBaseView):
    filename_prefix = 'laporan_mingguan'

    def get(self, request):
        minggu = request.query_params.get('minggu')
        tahun = request.query_params.get('tahun')
        data = export_weekly(minggu, tahun)
        filename = f'{self.filename_prefix}_m{minggu or "ini"}_t{tahun or "ini"}'
        return self._excel_response(data, filename)


@export_monthly_schema
class ExportMonthlyView(ExportBaseView):
    filename_prefix = 'laporan_bulanan'

    def get(self, request):
        bulan = request.query_params.get('bulan')
        tahun = request.query_params.get('tahun')
        data = export_monthly(bulan, tahun)
        filename = f'{self.filename_prefix}_b{bulan or "ini"}_t{tahun or "ini"}'
        return self._excel_response(data, filename)


@export_waste_schema
class ExportWasteView(ExportBaseView):
    filename_prefix = 'laporan_sampah'

    def get(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        data = export_waste(start, end)
        filename = f'{self.filename_prefix}_{start}_to_{end}'
        return self._excel_response(data, filename)


@export_evaluation_schema
class ExportEvaluationView(ExportBaseView):
    filename_prefix = 'laporan_evaluasi'

    def get(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        data = export_evaluation(start, end)
        filename = f'{self.filename_prefix}_{start}_to_{end}'
        return self._excel_response(data, filename)
