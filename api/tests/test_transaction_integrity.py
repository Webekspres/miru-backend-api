from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken

from api.models import KategoriSampah, MitraPengepul, PenarikanSaldo, PenjualanMitra
from api.services.ledger import (
    InsufficientPoinError,
    InsufficientSaldoError,
    InsufficientStokError,
    create_setoran_with_side_effects,
    credit_nasabah_setoran,
    debit_nasabah_saldo,
    debit_nasabah_poin,
    decrease_kategori_stok,
    increase_kategori_stok,
)

User = get_user_model()


class LedgerServiceTests(TestCase):
    def setUp(self):
        self.nasabah = User.objects.create_user(
            username='nasabah1',
            password='secret12',
            nama_lengkap='Nasabah Satu',
            role='nasabah',
            saldo=Decimal('100000.00'),
            poin=50,
        )
        self.petugas = User.objects.create_user(
            username='petugas1',
            password='secret12',
            nama_lengkap='Petugas Satu',
            role='petugas',
        )
        self.kategori = KategoriSampah.objects.create(
            nama='PET',
            harga_beli_per_kg=Decimal('3000.00'),
            stok_terkini_kg=Decimal('100.00'),
        )

    def test_credit_nasabah_setoran_updates_saldo_and_poin(self):
        credit_nasabah_setoran(self.nasabah, Decimal('5500.00'))
        self.nasabah.refresh_from_db()
        self.assertEqual(self.nasabah.saldo, Decimal('105500.00'))
        self.assertEqual(self.nasabah.poin, 55)

    def test_debit_nasabah_saldo_success(self):
        debit_nasabah_saldo(self.nasabah, Decimal('50000.00'))
        self.nasabah.refresh_from_db()
        self.assertEqual(self.nasabah.saldo, Decimal('50000.00'))

    def test_debit_nasabah_saldo_raises_when_insufficient(self):
        with self.assertRaises(InsufficientSaldoError):
            debit_nasabah_saldo(self.nasabah, Decimal('150000.00'))

    def test_debit_nasabah_poin_raises_when_insufficient(self):
        with self.assertRaises(InsufficientPoinError):
            debit_nasabah_poin(self.nasabah, 100)

    def test_increase_kategori_stok(self):
        increase_kategori_stok(self.kategori, Decimal('25.50'))
        self.kategori.refresh_from_db()
        self.assertEqual(self.kategori.stok_terkini_kg, Decimal('125.50'))

    def test_decrease_kategori_stok_success(self):
        decrease_kategori_stok(self.kategori, Decimal('40.00'))
        self.kategori.refresh_from_db()
        self.assertEqual(self.kategori.stok_terkini_kg, Decimal('60.00'))

    def test_decrease_kategori_stok_raises_when_insufficient(self):
        with self.assertRaises(InsufficientStokError):
            decrease_kategori_stok(self.kategori, Decimal('150.00'))

    def test_create_setoran_with_side_effects_atomically(self):
        transaksi = create_setoran_with_side_effects(
            {
                'nasabah': self.nasabah,
                'petugas': self.petugas,
            },
            [
                {
                    'kategori': self.kategori,
                    'berat_kg': Decimal('10.00'),
                    'harga_saat_itu': Decimal('3000.00'),
                    'subtotal': Decimal('30000.00'),
                },
            ],
        )
        self.nasabah.refresh_from_db()
        self.kategori.refresh_from_db()

        self.assertEqual(transaksi.total_nilai, Decimal('30000.00'))
        self.assertEqual(self.nasabah.saldo, Decimal('130000.00'))
        self.assertEqual(self.nasabah.poin, 80)
        self.assertEqual(self.kategori.stok_terkini_kg, Decimal('110.00'))
        self.assertEqual(transaksi.details.count(), 1)


class TransactionIntegrityAPITests(TestCase):
    """API-level tests for negative balance/stock guards."""

    def setUp(self):
        from rest_framework.test import APIClient

        self.client = APIClient()
        self.nasabah = User.objects.create_user(
            username='nasabah_api',
            password='secret12',
            nama_lengkap='Nasabah API',
            role='nasabah',
            saldo=Decimal('10000.00'),
        )
        self.admin = User.objects.create_user(
            username='admin_api',
            password='secret12',
            nama_lengkap='Admin API',
            role='admin',
        )
        self.kategori = KategoriSampah.objects.create(
            nama='Kardus',
            harga_beli_per_kg=Decimal('1500.00'),
            stok_terkini_kg=Decimal('5.00'),
        )
        self.mitra = MitraPengepul.objects.create(nama='Mitra A', kontak='08111')

    def _auth(self, user):
        token = AccessToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(token)}'
        )

    def test_partner_sale_rejects_insufficient_stock(self):
        self._auth(self.admin)
        response = self.client.post('/api/partner-sales/', {
            'mitra': self.mitra.pk,
            'kategori': self.kategori.pk,
            'berat_jual_kg': '10.00',
            'harga_jual_per_kg': '2000.00',
            'total_penjualan': '20000.00',
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.kategori.refresh_from_db()
        self.assertEqual(self.kategori.stok_terkini_kg, Decimal('5.00'))

    def test_withdrawal_completion_rejects_insufficient_saldo(self):
        penarikan = PenarikanSaldo.objects.create(
            nasabah=self.nasabah,
            nominal=Decimal('50000.00'),
            metode='transfer',
            status='menunggu',
        )
        self._auth(self.admin)
        response = self.client.patch(
            f'/api/withdrawals/{penarikan.pk}/',
            {'status': 'selesai'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.nasabah.refresh_from_db()
        self.assertEqual(self.nasabah.saldo, Decimal('10000.00'))

    def test_partner_sale_succeeds_with_sufficient_stock(self):
        self._auth(self.admin)
        response = self.client.post('/api/partner-sales/', {
            'mitra': self.mitra.pk,
            'kategori': self.kategori.pk,
            'berat_jual_kg': '3.00',
            'harga_jual_per_kg': '2000.00',
            'total_penjualan': '6000.00',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.kategori.refresh_from_db()
        self.assertEqual(self.kategori.stok_terkini_kg, Decimal('2.00'))
