from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework import status

from api.models import KategoriSampah, Pengumuman, RiwayatHarga

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

    def _future_date(self, days=4):
        """Helper: return a datetime H+4 from now (past H+3 minimum)."""
        return timezone.now() + timedelta(days=days)

    def test_price_change_creates_history_with_future_date(self):
        self.auth_as(self.admin)
        future = self._future_date()
        response = self.client.patch(
            f'/api/waste-categories/{self.category.id}/',
            {
                'harga_beli_per_kg': '3500.00',
                'tanggal_berlaku': future.isoformat(),
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Category price should NOT be updated immediately
        self.category.refresh_from_db()
        self.assertEqual(
            self.category.harga_beli_per_kg,
            Decimal('3000.00'),
            'harga_beli_per_kg tidak boleh berubah sampai tanggal_berlaku tiba',
        )

        # RiwayatHarga should be created with future date
        history = RiwayatHarga.objects.filter(kategori=self.category)
        self.assertEqual(history.count(), 1)
        entry = history.first()
        self.assertEqual(entry.harga_lama, Decimal('3000.00'))
        self.assertEqual(entry.harga_baru, Decimal('3500.00'))
        self.assertEqual(entry.diubah_oleh_id, self.admin.id)
        self.assertGreater(entry.tanggal_berlaku, timezone.now())

        # Pengumuman should be auto-created
        self.assertTrue(
            Pengumuman.objects.filter(judul__contains='PET').exists(),
            'Auto-pengumuman harus dibuat saat harga berubah',
        )

    def test_price_change_default_tanggal_berlaku(self):
        """If no tanggal_berlaku provided, default to H+3."""
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/waste-categories/{self.category.id}/',
            {'harga_beli_per_kg': '3500.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        entry = RiwayatHarga.objects.get(kategori=self.category)
        # Should be at least H+3 from the time of the test
        min_expected = timezone.now() + timedelta(hours=71)
        self.assertGreater(
            entry.tanggal_berlaku, min_expected,
            'Default tanggal_berlaku harus minimal H+3',
        )

    def test_reject_tanggal_berlaku_less_than_h3(self):
        """H+1 should be rejected."""
        self.auth_as(self.admin)
        too_soon = timezone.now() + timedelta(hours=24)  # H+1
        response = self.client.patch(
            f'/api/waste-categories/{self.category.id}/',
            {
                'harga_beli_per_kg': '3500.00',
                'tanggal_berlaku': too_soon.isoformat(),
            },
            format='json',
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            'Tanggal berlaku H+1 harus ditolak',
        )
        self.assertIn('tanggal_berlaku', str(response.data))
        self.assertEqual(
            RiwayatHarga.objects.filter(kategori=self.category).count(), 0,
        )

    def test_reject_tanggal_berlaku_in_past(self):
        """Tanggal di masa lalu harus ditolak."""
        self.auth_as(self.admin)
        past = timezone.now() - timedelta(days=1)
        response = self.client.patch(
            f'/api/waste-categories/{self.category.id}/',
            {
                'harga_beli_per_kg': '3500.00',
                'tanggal_berlaku': past.isoformat(),
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        future = self._future_date()
        self.client.patch(
            f'/api/waste-categories/{self.category.id}/',
            {
                'harga_beli_per_kg': '3200.00',
                'tanggal_berlaku': future.isoformat(),
            },
            format='json',
        )
        entry = RiwayatHarga.objects.get(kategori=self.category)
        self.assertEqual(entry.diubah_oleh_id, self.koordinator.id)

    def test_get_price_history_public(self):
        future = self._future_date()
        RiwayatHarga.objects.create(
            kategori=self.category,
            harga_lama=Decimal('3000.00'),
            harga_baru=Decimal('3500.00'),
            tanggal_berlaku=future,
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
        future = self._future_date()
        future2 = self._future_date(5)
        RiwayatHarga.objects.create(
            kategori=self.category,
            harga_lama=Decimal('3000.00'),
            harga_baru=Decimal('3200.00'),
            tanggal_berlaku=future,
            diubah_oleh=self.admin,
        )
        RiwayatHarga.objects.create(
            kategori=self.category,
            harga_lama=Decimal('3200.00'),
            harga_baru=Decimal('3500.00'),
            tanggal_berlaku=future2,
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

    def test_auto_pengumuman_contains_price_info(self):
        self.auth_as(self.admin)
        future = self._future_date()
        self.client.patch(
            f'/api/waste-categories/{self.category.id}/',
            {
                'harga_beli_per_kg': '5000.00',
                'tanggal_berlaku': future.isoformat(),
            },
            format='json',
        )
        pengumuman = Pengumuman.objects.filter(judul__contains='PET').first()
        self.assertIsNotNone(pengumuman)
        self.assertIn('Rp5', pengumuman.isi)
        self.assertIn('3,000', pengumuman.isi)
        self.assertEqual(pengumuman.judul, 'Perubahan Harga PET')
