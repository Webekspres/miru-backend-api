from decimal import Decimal

from django.utils import timezone
from rest_framework import status

from api.models import (
    KategoriSampah,
    MitraPengepul,
    PenjualanMitra,
    TransaksiSetoran,
)

from .base import EnvelopeAPITestCase


class InventoryTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin(username='admin_inv')
        self.nasabah = self.create_nasabah(username='nasabah_inv')
        KategoriSampah.objects.create(
            nama='PET', harga_beli_per_kg=Decimal('3000.00'), stok_terkini_kg=Decimal('10.00'),
        )
        KategoriSampah.objects.create(
            nama='Kardus', harga_beli_per_kg=Decimal('1500.00'), stok_terkini_kg=Decimal('4.00'),
        )

    def test_inventory_summary(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/inventory/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data['total_stok_kg'], '14.00')
        # 10*3000 + 4*1500 = 36000
        self.assertEqual(data['total_estimasi_nilai'], '36000.00')
        self.assertEqual(len(data['kategori']), 2)
        pet = next(k for k in data['kategori'] if k['nama'] == 'PET')
        self.assertEqual(pet['estimasi_nilai'], '30000.00')

    def test_pemerintah_can_read(self):
        self.auth_as(self.create_pemerintah(username='pem_inv'))
        response = self.client.get('/api/inventory/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nasabah_forbidden(self):
        self.auth_as(self.nasabah)
        response = self.client.get('/api/inventory/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class InventoryHistoryTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin(username='admin_inv_hist')
        self.nasabah = self.create_nasabah(username='nasabah_inv_hist')
        self.petugas = self.create_petugas(username='petugas_inv_hist')
        self.kategori = KategoriSampah.objects.create(
            nama='PET', harga_beli_per_kg=Decimal('3000.00'), stok_terkini_kg=Decimal('55.00'),
        )
        self.mitra = MitraPengepul.objects.create(nama='PT Pengepul', kontak='08111')

        deposit = TransaksiSetoran.objects.create(
            nasabah=self.nasabah,
            petugas=self.petugas,
            total_nilai=Decimal('15000.00'),
            status='selesai',
        )
        self.detail = deposit.details.create(
            kategori=self.kategori,
            berat_kg=Decimal('5.00'),
            harga_saat_itu=Decimal('3000.00'),
            subtotal=Decimal('15000.00'),
        )
        TransaksiSetoran.objects.filter(pk=deposit.pk).update(
            tanggal=timezone.now() - timezone.timedelta(days=2),
        )

        self.sale = PenjualanMitra.objects.create(
            mitra=self.mitra,
            kategori=self.kategori,
            berat_jual_kg=Decimal('10.00'),
            harga_jual_per_kg=Decimal('2500.00'),
            total_penjualan=Decimal('25000.00'),
        )
        PenjualanMitra.objects.filter(pk=self.sale.pk).update(
            tanggal=timezone.now() - timezone.timedelta(days=1),
        )

    def test_history_merges_masuk_and_keluar(self):
        self.auth_as(self.admin)
        response = self.client.get(f'/api/inventory/{self.kategori.id}/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data['kategori_id'], self.kategori.id)
        self.assertEqual(data['nama'], 'PET')
        self.assertEqual(len(data['history']), 2)

        # Terbaru dulu: penjualan (1 hari lalu) lalu setoran (2 hari lalu)
        self.assertEqual(data['history'][0]['arah'], 'keluar')
        self.assertEqual(data['history'][0]['sumber'], 'penjualan_mitra')
        self.assertEqual(data['history'][0]['berat_kg'], '10.00')
        self.assertEqual(data['history'][1]['arah'], 'masuk')
        self.assertEqual(data['history'][1]['sumber'], 'setoran')
        self.assertEqual(data['history'][1]['berat_kg'], '5.00')
        self.assertEqual(data['history'][1]['id'], self.detail.id)

    def test_history_limit_param(self):
        self.auth_as(self.admin)
        response = self.client.get(
            f'/api/inventory/{self.kategori.id}/history/?limit=1'
        )
        self.assertEqual(len(response.data['data']['history']), 1)

    def test_history_unknown_kategori_404(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/inventory/99999/history/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_history_empty(self):
        kosong = KategoriSampah.objects.create(
            nama='Kaca', harga_beli_per_kg=Decimal('500.00'),
        )
        self.auth_as(self.admin)
        response = self.client.get(f'/api/inventory/{kosong.id}/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['history'], [])

    def test_pemerintah_can_read_history(self):
        self.auth_as(self.create_pemerintah(username='pem_inv_hist'))
        response = self.client.get(f'/api/inventory/{self.kategori.id}/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nasabah_forbidden_history(self):
        self.auth_as(self.nasabah)
        response = self.client.get(f'/api/inventory/{self.kategori.id}/history/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
