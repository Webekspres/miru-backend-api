from decimal import Decimal

from django.utils import timezone
from datetime import timedelta
from rest_framework import status

from api.models import (
    KategoriSampah,
    MitraPengepul,
    PenarikanSaldo,
    Penjemputan,
    PenukaranPoin,
    Pengaduan,
    Reward,
    TransaksiSetoran,
)

from .base import EnvelopeAPITestCase


class NasabahDataIsolationTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah_a = self.create_nasabah(username='nasabah_iso_a')
        self.nasabah_b = self.create_nasabah(username='nasabah_iso_b')
        self.kategori = KategoriSampah.objects.create(
            nama='Kertas', harga_beli_per_kg=Decimal('2000.00'),
        )
        TransaksiSetoran.objects.create(
            nasabah=self.nasabah_a, total_nilai=Decimal('10000.00'),
        )
        TransaksiSetoran.objects.create(
            nasabah=self.nasabah_b, total_nilai=Decimal('20000.00'),
        )
        Penjemputan.objects.create(
            nasabah=self.nasabah_a,
            estimasi_berat=Decimal('10.00'),
            alamat_jemput='A',
            jadwal='2026-08-01T09:00:00+09:00',
        )
        Pengaduan.objects.create(
            nasabah=self.nasabah_b,
            jenis_pengaduan='kesalahan_data',
            keluhan='Test',
        )

    def test_nasabah_sees_only_own_deposits(self):
        self.auth_as(self.nasabah_a)
        response = self.client.get('/api/deposits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['nasabah'], self.nasabah_a.id)

    def test_nasabah_sees_only_own_pickups(self):
        self.auth_as(self.nasabah_a)
        response = self.client.get('/api/pickups/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)


class KoordinatorAccessTests(EnvelopeAPITestCase):
    def setUp(self):
        self.koordinator = self.create_koordinator(username='koord_role')
        self.nasabah = self.create_nasabah(username='nasabah_role')
        self.nasabah.saldo = Decimal('200000.00')
        self.nasabah.save()
        self.withdrawal = PenarikanSaldo.objects.create(
            nasabah=self.nasabah,
            nominal=Decimal('50000.00'),
            metode='tunai',
            status='menunggu',
        )
        self.reward = Reward.objects.create(nama='Bibit', poin_dibutuhkan=50, stok=5)
        PenukaranPoin.objects.create(
            nasabah=self.nasabah, reward=self.reward, status='menunggu',
        )

    def test_koordinator_can_list_redemptions(self):
        self.auth_as(self.koordinator)
        response = self.client.get('/api/reward-redemptions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_koordinator_can_approve_withdrawal(self):
        self.auth_as(self.koordinator)
        response = self.client.patch(
            f'/api/withdrawals/{self.withdrawal.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_koordinator_cannot_approve_redemption(self):
        redemption = PenukaranPoin.objects.get(nasabah=self.nasabah)
        self.auth_as(self.koordinator)
        response = self.client.patch(
            f'/api/reward-redemptions/{redemption.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PemerintahReadOnlyTests(EnvelopeAPITestCase):
    def setUp(self):
        self.pemerintah = self.create_pemerintah()
        self.admin = self.create_admin(username='admin_role')
        self.nasabah = self.create_nasabah(username='nasabah_role2')
        TransaksiSetoran.objects.create(
            nasabah=self.nasabah, total_nilai=Decimal('5000.00'),
        )
        MitraPengepul.objects.create(nama='Mitra X', kontak='08111')

    def test_pemerintah_can_list_deposits(self):
        self.auth_as(self.pemerintah)
        response = self.client.get('/api/deposits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_pemerintah_can_list_partners(self):
        self.auth_as(self.pemerintah)
        response = self.client.get('/api/partners/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pemerintah_cannot_create_partner(self):
        self.auth_as(self.pemerintah)
        response = self.client.post('/api/partners/', {
            'nama': 'Blocked', 'kontak': '08111',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pemerintah_cannot_create_deposit(self):
        self.auth_as(self.pemerintah)
        response = self.client.post('/api/deposits/', {
            'nasabah': self.nasabah.id,
            'details': [],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PetugasAccessTests(EnvelopeAPITestCase):
    def setUp(self):
        self.petugas = self.create_petugas(username='petugas_role')
        self.nasabah = self.create_nasabah(username='nasabah_role3')
        self.kategori = KategoriSampah.objects.create(
            nama='PET', harga_beli_per_kg=Decimal('3000.00'),
        )
        self.pickup = Penjemputan.objects.create(
            nasabah=self.nasabah,
            petugas=self.petugas,
            estimasi_berat=Decimal('10.00'),
            alamat_jemput='Timika',
            jadwal=(timezone.now() + timedelta(days=2)).replace(
                hour=9, minute=0, second=0, microsecond=0,
            ),
            status='dijadwalkan',
        )

    def test_petugas_can_create_deposit(self):
        self.auth_as(self.petugas)
        response = self.client.post('/api/deposits/', {
            'nasabah': self.nasabah.id,
            'details': [{'kategori': self.kategori.id, 'berat_kg': '5.00'}],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_petugas_can_update_assigned_pickup(self):
        self.auth_as(self.petugas)
        response = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'dalam_perjalanan'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
