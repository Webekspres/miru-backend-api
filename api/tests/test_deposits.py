from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework import status

from api.models import KategoriSampah, TransaksiSetoran

from .base import EnvelopeAPITestCase


class DepositCreateTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah(username='nasabah_dep')
        self.petugas = self.create_petugas()
        self.admin = self.create_admin(username='admin_dep')
        self.koordinator = self.create_koordinator(username='koord_dep')
        self.kategori_pet = KategoriSampah.objects.create(
            nama='PET',
            harga_beli_per_kg=Decimal('3000.00'),
        )
        self.kategori_kardus = KategoriSampah.objects.create(
            nama='Kardus',
            harga_beli_per_kg=Decimal('1500.00'),
        )

    def _deposit_payload(self, **overrides):
        payload = {
            'nasabah': self.nasabah.id,
            'details': [
                {'kategori': self.kategori_pet.id, 'berat_kg': '5.00'},
                {'kategori': self.kategori_kardus.id, 'berat_kg': '3.50'},
            ],
        }
        payload.update(overrides)
        return payload

    def test_create_as_petugas_success(self):
        self.auth_as(self.petugas)
        response = self.client.post(
            '/api/deposits/', self._deposit_payload(), format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data['data']
        self.assertEqual(data['total_nilai'], '20250.00')
        self.assertEqual(data['petugas'], self.petugas.id)
        self.assertEqual(data['status'], 'selesai')
        self.assertEqual(len(data['details']), 2)
        self.assertEqual(data['details'][0]['harga_saat_itu'], '3000.00')
        self.assertEqual(data['details'][0]['subtotal'], '15000.00')
        self.assertEqual(data['poin_didapat'], 20)
        self.assertEqual(data['saldo_nasabah_baru'], '20250.00')

        self.nasabah.refresh_from_db()
        self.kategori_pet.refresh_from_db()
        self.kategori_kardus.refresh_from_db()
        self.assertEqual(self.nasabah.saldo, Decimal('20250.00'))
        self.assertEqual(self.nasabah.poin, 20)
        self.assertEqual(self.kategori_pet.stok_terkini_kg, Decimal('5.00'))
        self.assertEqual(self.kategori_kardus.stok_terkini_kg, Decimal('3.50'))

    def test_create_as_admin_success(self):
        self.auth_as(self.admin)
        response = self.client.post(
            '/api/deposits/', self._deposit_payload(), format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_nasabah_cannot_create_deposit(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/deposits/', self._deposit_payload(), format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_koordinator_cannot_create_deposit(self):
        self.auth_as(self.koordinator)
        response = self.client.post(
            '/api/deposits/', self._deposit_payload(), format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reject_weight_below_1kg(self):
        self.auth_as(self.petugas)
        response = self.client.post(
            '/api/deposits/',
            self._deposit_payload(details=[
                {'kategori': self.kategori_pet.id, 'berat_kg': '0.50'},
            ]),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_reject_inactive_nasabah(self):
        self.nasabah.is_active = False
        self.nasabah.save()
        self.auth_as(self.petugas)
        response = self.client.post(
            '/api/deposits/', self._deposit_payload(), format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_non_nasabah_user(self):
        self.auth_as(self.petugas)
        response = self.client.post(
            '/api/deposits/',
            self._deposit_payload(nasabah=self.petugas.id),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_auto_calculate_price_ignores_client_values(self):
        self.auth_as(self.petugas)
        payload = self._deposit_payload()
        payload['details'][0]['harga_saat_itu'] = '9999.00'
        payload['details'][0]['subtotal'] = '99999.00'
        response = self.client.post('/api/deposits/', payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['total_nilai'], '20250.00')


class DepositReadFilterTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah_a = self.create_nasabah(username='nasabah_a')
        self.nasabah_b = self.create_nasabah(username='nasabah_b')
        self.petugas = self.create_petugas()
        self.kategori = KategoriSampah.objects.create(
            nama='Kertas',
            harga_beli_per_kg=Decimal('2000.00'),
        )
        self.auth_as(self.petugas)
        self.client.post('/api/deposits/', {
            'nasabah': self.nasabah_a.id,
            'details': [{'kategori': self.kategori.id, 'berat_kg': '2.00'}],
        }, format='json')
        self.client.post('/api/deposits/', {
            'nasabah': self.nasabah_b.id,
            'details': [{'kategori': self.kategori.id, 'berat_kg': '3.00'}],
        }, format='json')

        old = TransaksiSetoran.objects.filter(nasabah=self.nasabah_a).first()
        TransaksiSetoran.objects.filter(pk=old.pk).update(
            tanggal=timezone.now() - timedelta(days=10),
        )

    def test_retrieve_includes_nested_details(self):
        transaksi = TransaksiSetoran.objects.filter(nasabah=self.nasabah_a).first()
        self.auth_as(self.nasabah_a)
        response = self.client.get(f'/api/deposits/{transaksi.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('details', response.data['data'])
        self.assertEqual(len(response.data['data']['details']), 1)

    def test_nasabah_only_sees_own_deposits(self):
        self.auth_as(self.nasabah_a)
        response = self.client.get('/api/deposits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item['nasabah'] for item in response.data['data']}
        self.assertEqual(ids, {self.nasabah_a.id})

    def test_filter_by_nasabah(self):
        self.auth_as(self.petugas)
        response = self.client.get(
            f'/api/deposits/?nasabah={self.nasabah_b.id}',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(
            item['nasabah'] == self.nasabah_b.id for item in response.data['data']
        ))

    def test_filter_by_tanggal_after(self):
        self.auth_as(self.petugas)
        cutoff = (timezone.now() - timedelta(days=5)).date().isoformat()
        response = self.client.get(f'/api/deposits/?tanggal_after={cutoff}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['nasabah'], self.nasabah_b.id)

    def test_ordering_by_tanggal_desc(self):
        self.auth_as(self.petugas)
        response = self.client.get('/api/deposits/?ordering=-tanggal')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tanggal_list = [item['tanggal'] for item in response.data['data']]
        self.assertEqual(tanggal_list, sorted(tanggal_list, reverse=True))
