from decimal import Decimal

from rest_framework import status

from api.models import KategoriSampah, MitraPengepul, PenjualanMitra

from .base import EnvelopeAPITestCase


class MitraPengepulCrudTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin(username='admin_mitra')
        self.koordinator = self.create_koordinator(username='koord_mitra')
        self.nasabah = self.create_nasabah(username='nasabah_mitra')

    def test_admin_create_mitra(self):
        self.auth_as(self.admin)
        response = self.client.post('/api/partners/', {
            'nama': 'PT Pengepul Timika',
            'kontak': '08123456789',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['nama'], 'PT Pengepul Timika')

    def test_koordinator_can_create_mitra(self):
        self.auth_as(self.koordinator)
        response = self.client.post('/api/partners/', {
            'nama': 'Mitra Koordinator',
            'kontak': '08111',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_nasabah_cannot_access_partners(self):
        self.auth_as(self.nasabah)
        response = self.client.get('/api/partners/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reject_duplicate_nama(self):
        MitraPengepul.objects.create(nama='PT Duplikat', kontak='08111')
        self.auth_as(self.admin)
        response = self.client.post('/api/partners/', {
            'nama': 'PT Duplikat',
            'kontak': '08122',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PartnerSaleTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin(username='admin_sale')
        self.koordinator = self.create_koordinator(username='koord_sale')
        self.nasabah = self.create_nasabah(username='nasabah_sale')
        self.mitra = MitraPengepul.objects.create(
            nama='PT Pengepul', kontak='08111',
        )
        self.kategori = KategoriSampah.objects.create(
            nama='PET',
            harga_beli_per_kg=Decimal('3000.00'),
            stok_terkini_kg=Decimal('100.00'),
        )

    def _payload(self, **overrides):
        payload = {
            'mitra': self.mitra.id,
            'kategori': self.kategori.id,
            'berat_jual_kg': '40.00',
            'harga_jual_per_kg': '2500.00',
        }
        payload.update(overrides)
        return payload

    def test_create_sale_success(self):
        self.auth_as(self.admin)
        response = self.client.post('/api/partner-sales/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data['data']
        self.assertEqual(data['total_penjualan'], '100000.00')
        self.assertEqual(data['stok_kategori_baru'], '60.00')
        self.assertEqual(data['mitra_nama'], 'PT Pengepul')
        self.assertEqual(data['kategori_nama'], 'PET')

        self.kategori.refresh_from_db()
        self.assertEqual(self.kategori.stok_terkini_kg, Decimal('60.00'))
        self.assertEqual(PenjualanMitra.objects.count(), 1)

    def test_auto_calculate_total_ignores_client(self):
        self.auth_as(self.admin)
        payload = self._payload()
        payload['total_penjualan'] = '999999.00'
        response = self.client.post('/api/partner-sales/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['total_penjualan'], '100000.00')

    def test_reject_insufficient_stok(self):
        self.auth_as(self.admin)
        response = self.client.post(
            '/api/partner-sales/',
            self._payload(berat_jual_kg='150.00'),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.kategori.refresh_from_db()
        self.assertEqual(self.kategori.stok_terkini_kg, Decimal('100.00'))

    def test_reject_zero_berat(self):
        self.auth_as(self.admin)
        response = self.client.post(
            '/api/partner-sales/',
            self._payload(berat_jual_kg='0.00'),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_koordinator_can_create_sale(self):
        self.auth_as(self.koordinator)
        response = self.client.post('/api/partner-sales/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_nasabah_cannot_create_sale(self):
        self.auth_as(self.nasabah)
        response = self.client.post('/api/partner-sales/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_mitra(self):
        PenjualanMitra.objects.create(
            mitra=self.mitra,
            kategori=self.kategori,
            berat_jual_kg=Decimal('10.00'),
            harga_jual_per_kg=Decimal('2000.00'),
            total_penjualan=Decimal('20000.00'),
        )
        other_mitra = MitraPengepul.objects.create(nama='Mitra Lain', kontak='08222')
        PenjualanMitra.objects.create(
            mitra=other_mitra,
            kategori=self.kategori,
            berat_jual_kg=Decimal('5.00'),
            harga_jual_per_kg=Decimal('2000.00'),
            total_penjualan=Decimal('10000.00'),
        )
        self.auth_as(self.admin)
        response = self.client.get(f'/api/partner-sales/?mitra={self.mitra.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
