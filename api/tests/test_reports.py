from datetime import datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.conf import settings
from rest_framework import status

from api.models import (
    KategoriSampah,
    PenarikanSaldo,
    TransaksiSetoran,
)

from .base import EnvelopeAPITestCase, User

TZ = ZoneInfo(settings.TIME_ZONE)


class ReportTestMixin:
    def _aware(self, y, m, d):
        return datetime.combine(datetime(y, m, d), time(10, 0), tzinfo=TZ)

    def _build(self):
        self.nasabah = self.create_nasabah(username='nasabah_rep')
        User.objects.filter(pk=self.nasabah.pk).update(date_joined=self._aware(2026, 7, 7))
        self.petugas = self.create_petugas(username='petugas_rep')
        self.admin = self.create_admin(username='admin_rep')

        self.pet = KategoriSampah.objects.create(
            nama='PET', harga_beli_per_kg=Decimal('3000.00'),
        )
        self.kardus = KategoriSampah.objects.create(
            nama='Kardus', harga_beli_per_kg=Decimal('1500.00'),
        )

        # Setoran on 2026-07-07 (10 kg PET = 30000, 4 kg kardus = 6000)
        dep = TransaksiSetoran.objects.create(
            nasabah=self.nasabah, petugas=self.petugas,
            total_nilai=Decimal('36000.00'), status='selesai',
        )
        dep.details.create(
            kategori=self.pet, berat_kg=Decimal('10.00'),
            harga_saat_itu=Decimal('3000.00'), subtotal=Decimal('30000.00'),
        )
        dep.details.create(
            kategori=self.kardus, berat_kg=Decimal('4.00'),
            harga_saat_itu=Decimal('1500.00'), subtotal=Decimal('6000.00'),
        )
        TransaksiSetoran.objects.filter(pk=dep.pk).update(tanggal=self._aware(2026, 7, 7))

        wd = PenarikanSaldo.objects.create(
            nasabah=self.nasabah, nominal=Decimal('50000.00'),
            metode='tunai', status='selesai',
        )
        PenarikanSaldo.objects.filter(pk=wd.pk).update(tanggal=self._aware(2026, 7, 7))


class DailyReportTests(ReportTestMixin, EnvelopeAPITestCase):
    def setUp(self):
        self._build()

    def test_daily_report(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/reports/daily/?tanggal=2026-07-07')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data['jumlah_transaksi'], 1)
        self.assertEqual(data['total_setoran'], '36000.00')
        self.assertEqual(data['total_penarikan'], '50000.00')
        self.assertEqual(data['total_sampah_kg'], '14.00')
        self.assertEqual(len(data['tonase_per_jenis']), 2)

    def test_daily_empty_other_day(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/reports/daily/?tanggal=2026-07-08')
        self.assertEqual(response.data['data']['jumlah_transaksi'], 0)
        self.assertEqual(response.data['data']['total_setoran'], '0.00')

    def test_daily_missing_param_400(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/reports/daily/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_daily_invalid_format_400(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/reports/daily/?tanggal=07-07-2026')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nasabah_forbidden(self):
        self.auth_as(self.nasabah)
        response = self.client.get('/api/reports/daily/?tanggal=2026-07-07')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class WeeklyReportTests(ReportTestMixin, EnvelopeAPITestCase):
    def setUp(self):
        self._build()

    def test_weekly_report(self):
        # 2026-07-07 is in ISO week 28
        self.auth_as(self.admin)
        response = self.client.get('/api/reports/weekly/?minggu=28&tahun=2026')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data['jumlah_transaksi'], 1)
        self.assertEqual(data['total_setoran'], '36000.00')
        self.assertIn('periode', data)
        self.assertEqual(data['nasabah_baru'], 1)

    def test_invalid_week_400(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/reports/weekly/?minggu=99&tahun=2026')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MonthlyReportTests(ReportTestMixin, EnvelopeAPITestCase):
    def setUp(self):
        self._build()

    def test_monthly_report(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/reports/monthly/?bulan=7&tahun=2026')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data['jumlah_nasabah_terdaftar'], 1)
        self.assertEqual(data['jumlah_nasabah_aktif'], 1)
        self.assertEqual(data['total_nilai_setoran'], '36000.00')
        self.assertEqual(data['total_sampah_kg'], '14.00')
        self.assertEqual(len(data['tonase_per_jenis']), 2)

    def test_invalid_month_400(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/reports/monthly/?bulan=0&tahun=2026')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class WasteReportTests(ReportTestMixin, EnvelopeAPITestCase):
    def setUp(self):
        self._build()

    def test_waste_report(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/reports/waste/?start=2026-07-01&end=2026-07-31')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data['total_berat_kg'], '14.00')
        self.assertEqual(data['total_nilai'], '36000.00')
        self.assertEqual(len(data['per_kategori']), 2)

    def test_waste_start_after_end_400(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/reports/waste/?start=2026-07-31&end=2026-07-01')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EvaluationReportTests(ReportTestMixin, EnvelopeAPITestCase):
    def setUp(self):
        self._build()

    def test_evaluation_report(self):
        self.auth_as(self.admin)
        response = self.client.get(
            '/api/reports/evaluation/?start=2026-07-01&end=2026-07-31'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data['jumlah_nasabah_aktif'], 1)
        self.assertEqual(data['total_nilai_setoran'], '36000.00')
        self.assertIn('total_poin_ditukar', data)
