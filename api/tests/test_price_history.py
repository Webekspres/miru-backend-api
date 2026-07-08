from decimal import Decimal

from rest_framework import status

from api.models import KategoriSampah, RiwayatHarga

from .base import EnvelopeAPITestCase


class PriceHistoryTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin(username='admin_price_hist')
        self.koordinator = self.create_koordinator(username='koord_price_hist')
        self.nasabah = self.create_nasabah(username='nasabah_price_hist')
        self.category = KategoriSampah.objects.create(
            nama='PET',
            harga_beli_per_kg=Decimal('3000.00'),
        )

    def test_price_change_creates_history(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/waste-categories/{self.category.id}/',
            {'harga_beli_per_kg': '3500.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        history = RiwayatHarga.objects.filter(kategori=self.category)
        self.assertEqual(history.count(), 1)
        entry = history.first()
        self.assertEqual(entry.harga_lama, Decimal('3000.00'))
        self.assertEqual(entry.harga_baru, Decimal('3500.00'))
        self.assertEqual(entry.diubah_oleh_id, self.admin.id)

    def test_no_history_when_price_unchanged(self):
        self.auth_as(self.admin)
        self.client.patch(
            f'/api/waste-categories/{self.category.id}/',
            {'nama': 'PET Botol'},
            format='json',
        )
        self.assertEqual(RiwayatHarga.objects.filter(kategori=self.category).count(), 0)

    def test_koordinator_change_also_recorded(self):
        self.auth_as(self.koordinator)
        self.client.patch(
            f'/api/waste-categories/{self.category.id}/',
            {'harga_beli_per_kg': '3200.00'},
            format='json',
        )
        entry = RiwayatHarga.objects.get(kategori=self.category)
        self.assertEqual(entry.diubah_oleh_id, self.koordinator.id)

    def test_get_price_history_public(self):
        RiwayatHarga.objects.create(
            kategori=self.category,
            harga_lama=Decimal('3000.00'),
            harga_baru=Decimal('3500.00'),
            diubah_oleh=self.admin,
        )
        response = self.client.get(
            f'/api/waste-categories/{self.category.id}/price-history/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response)
        self.assertEqual(len(response.data['data']), 1)
        item = response.data['data'][0]
        self.assertEqual(item['harga_lama'], '3000.00')
        self.assertEqual(item['harga_baru'], '3500.00')
        self.assertEqual(item['diubah_oleh_nama'], self.admin.nama_lengkap)

    def test_price_history_ordered_newest_first(self):
        RiwayatHarga.objects.create(
            kategori=self.category,
            harga_lama=Decimal('3000.00'),
            harga_baru=Decimal('3200.00'),
            diubah_oleh=self.admin,
        )
        RiwayatHarga.objects.create(
            kategori=self.category,
            harga_lama=Decimal('3200.00'),
            harga_baru=Decimal('3500.00'),
            diubah_oleh=self.admin,
        )
        response = self.client.get(
            f'/api/waste-categories/{self.category.id}/price-history/',
        )
        data = response.data['data']
        self.assertEqual(data[0]['harga_baru'], '3500.00')
        self.assertEqual(data[1]['harga_baru'], '3200.00')

    def test_price_history_unknown_category_404(self):
        response = self.client.get('/api/waste-categories/99999/price-history/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
