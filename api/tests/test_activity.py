from decimal import Decimal

from django.utils import timezone
from rest_framework import status

from api.models import (
    KategoriSampah,
    PenarikanSaldo,
    PenukaranPoin,
    Reward,
    TransaksiSetoran,
)

from .base import EnvelopeAPITestCase


class ActivityListTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah_a = self.create_nasabah(username='nasabah_act_a')
        self.nasabah_b = self.create_nasabah(username='nasabah_act_b')
        self.admin = self.create_admin(username='admin_act')
        self.petugas = self.create_petugas()

        kategori = KategoriSampah.objects.create(
            nama='PET', harga_beli_per_kg=Decimal('3000.00'),
        )
        self.deposit = TransaksiSetoran.objects.create(
            nasabah=self.nasabah_a,
            petugas=self.petugas,
            total_nilai=Decimal('15000.00'),
            status='selesai',
        )
        self.deposit.details.create(
            kategori=kategori,
            berat_kg=Decimal('5.00'),
            harga_saat_itu=Decimal('3000.00'),
            subtotal=Decimal('15000.00'),
        )
        self.withdrawal = PenarikanSaldo.objects.create(
            nasabah=self.nasabah_a,
            nominal=Decimal('50000.00'),
            metode='tunai',
            status='selesai',
        )
        self.reward = Reward.objects.create(
            nama='Pulsa Rp10.000', poin_dibutuhkan=100, stok=5,
        )
        self.redemption = PenukaranPoin.objects.create(
            nasabah=self.nasabah_a,
            reward=self.reward,
            status='selesai',
        )
        TransaksiSetoran.objects.create(
            nasabah=self.nasabah_b,
            petugas=self.petugas,
            total_nilai=Decimal('9000.00'),
            status='selesai',
        )

    def test_nasabah_sees_merged_activity(self):
        self.auth_as(self.nasabah_a)
        response = self.client.get('/api/activity/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 3)
        types = {item['type'] for item in response.data['data']}
        self.assertEqual(types, {'setoran', 'penarikan', 'penukaran_poin'})
        self.assertIn('pagination', response.data['meta'])

    def test_each_item_has_type_field(self):
        self.auth_as(self.nasabah_a)
        response = self.client.get('/api/activity/')
        for item in response.data['data']:
            self.assertIn('type', item)
            self.assertIn('tanggal', item)
            self.assertIn('status', item)
            self.assertIn('keterangan', item)

    def test_filter_jenis_setoran(self):
        self.auth_as(self.nasabah_a)
        response = self.client.get('/api/activity/?jenis=setoran')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['type'], 'setoran')
        self.assertEqual(response.data['data'][0]['nominal'], '15000.00')

    def test_filter_jenis_penarikan(self):
        self.auth_as(self.nasabah_a)
        response = self.client.get('/api/activity/?jenis=penarikan')
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['type'], 'penarikan')

    def test_filter_jenis_poin(self):
        self.auth_as(self.nasabah_a)
        response = self.client.get('/api/activity/?jenis=poin')
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['type'], 'penukaran_poin')
        self.assertEqual(response.data['data'][0]['poin'], 100)
        self.assertIsNone(response.data['data'][0]['nominal'])

    def test_invalid_jenis_returns_400(self):
        self.auth_as(self.nasabah_a)
        response = self.client.get('/api/activity/?jenis=invalid')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ordering_tanggal_desc(self):
        old = timezone.now() - timezone.timedelta(days=5)
        TransaksiSetoran.objects.filter(pk=self.deposit.pk).update(tanggal=old)

        self.auth_as(self.nasabah_a)
        response = self.client.get('/api/activity/?ordering=-tanggal')
        tanggal_list = [item['tanggal'] for item in response.data['data']]
        self.assertEqual(tanggal_list, sorted(tanggal_list, reverse=True))

    def test_pagination_page_param(self):
        self.auth_as(self.nasabah_a)
        response = self.client.get('/api/activity/?page=1&page_size=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
        self.assertEqual(response.data['meta']['pagination']['count'], 3)

    def test_nasabah_only_sees_own_activity(self):
        self.auth_as(self.nasabah_a)
        response = self.client.get('/api/activity/')
        self.assertEqual(len(response.data['data']), 3)

        self.auth_as(self.nasabah_b)
        response_b = self.client.get('/api/activity/')
        self.assertEqual(len(response_b.data['data']), 1)
        self.assertEqual(response_b.data['data'][0]['type'], 'setoran')

    def test_petugas_cannot_access(self):
        self.auth_as(self.petugas)
        response = self.client.get('/api/activity/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_filter_by_nasabah(self):
        self.auth_as(self.admin)
        response = self.client.get(f'/api/activity/?nasabah={self.nasabah_b.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
