from decimal import Decimal

from django.utils import timezone
from rest_framework import status

from api.models import (
    KategoriSampah,
    PenarikanSaldo,
    Penjemputan,
    Pengaduan,
    PenukaranPoin,
    Reward,
    TransaksiSetoran,
)

from .base import EnvelopeAPITestCase


class DashboardTestMixin:
    def _build_data(self):
        self.nasabah = self.create_nasabah(username='nasabah_dash')
        self.petugas = self.create_petugas(username='petugas_dash')

        self.pet = KategoriSampah.objects.create(
            nama='PET', harga_beli_per_kg=Decimal('3000.00'), stok_terkini_kg=Decimal('10.00'),
        )
        self.kardus = KategoriSampah.objects.create(
            nama='Kardus', harga_beli_per_kg=Decimal('1500.00'), stok_terkini_kg=Decimal('4.00'),
        )

        deposit = TransaksiSetoran.objects.create(
            nasabah=self.nasabah, petugas=self.petugas,
            total_nilai=Decimal('15000.00'), status='selesai',
        )
        deposit.details.create(
            kategori=self.pet, berat_kg=Decimal('5.00'),
            harga_saat_itu=Decimal('3000.00'), subtotal=Decimal('15000.00'),
        )

        PenarikanSaldo.objects.create(
            nasabah=self.nasabah, nominal=Decimal('50000.00'),
            metode='tunai', status='selesai',
        )
        Penjemputan.objects.create(
            nasabah=self.nasabah, estimasi_berat=Decimal('8.00'),
            alamat_jemput='Timika', jadwal=timezone.now(), status='menunggu',
        )
        reward = Reward.objects.create(nama='Pulsa', poin_dibutuhkan=100, stok=5)
        PenukaranPoin.objects.create(
            nasabah=self.nasabah, reward=reward, status='selesai',
        )
        Pengaduan.objects.create(
            nasabah=self.nasabah, jenis_pengaduan='saldo_belum_masuk',
            keluhan='Saldo belum masuk', status='terbuka',
        )


class DashboardOverviewTests(DashboardTestMixin, EnvelopeAPITestCase):
    def setUp(self):
        self._build_data()
        self.admin = self.create_admin(username='admin_dash')

    def test_overview_returns_aggregates(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/dashboard/overview/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data['total_nasabah'], 1)
        self.assertEqual(data['nasabah_aktif_30_hari'], 1)
        self.assertEqual(data['total_sampah_kg'], '5.00')
        self.assertEqual(data['total_nilai_setoran'], '15000.00')
        self.assertEqual(data['total_penarikan'], '50000.00')
        self.assertEqual(data['total_penukaran_poin'], 1)
        self.assertEqual(data['penjemputan_menunggu'], 1)
        self.assertEqual(data['pengaduan_terbuka'], 1)
        self.assertEqual(len(data['stok_per_kategori']), 2)

    def test_pemerintah_can_read(self):
        self.auth_as(self.create_pemerintah(username='pem_dash'))
        response = self.client.get('/api/dashboard/overview/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nasabah_forbidden(self):
        self.auth_as(self.nasabah)
        response = self.client.get('/api/dashboard/overview/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_petugas_forbidden(self):
        self.auth_as(self.petugas)
        response = self.client.get('/api/dashboard/overview/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_401(self):
        response = self.client.get('/api/dashboard/overview/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DashboardDepositChartTests(DashboardTestMixin, EnvelopeAPITestCase):
    def setUp(self):
        self._build_data()
        self.admin = self.create_admin(username='admin_chart')

    def test_chart_returns_full_month(self):
        now = timezone.localtime(timezone.now())
        self.auth_as(self.admin)
        response = self.client.get(
            f'/api/dashboard/deposit-chart/?bulan={now.month}&tahun={now.year}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data['bulan'], now.month)
        self.assertGreaterEqual(len(data['data']), 28)
        today_iso = now.date().isoformat()
        today_row = next(r for r in data['data'] if r['tanggal'] == today_iso)
        self.assertEqual(today_row['jumlah_transaksi'], 1)
        self.assertEqual(today_row['total_nilai'], '15000.00')

    def test_invalid_bulan_returns_400(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/dashboard/deposit-chart/?bulan=13&tahun=2026')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DashboardRecentActivityTests(DashboardTestMixin, EnvelopeAPITestCase):
    def setUp(self):
        self._build_data()
        self.admin = self.create_admin(username='admin_recent')

    def test_recent_activity_default_limit(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/dashboard/recent-activity/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        types = {item['type'] for item in data}
        self.assertTrue(types.issubset({'setoran', 'penarikan', 'penjemputan'}))
        for item in data:
            self.assertIn('tanggal', item)
            self.assertIn('type', item)

    def test_limit_param(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/dashboard/recent-activity/?limit=1')
        self.assertEqual(len(response.data['data']), 1)
