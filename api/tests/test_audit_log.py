from decimal import Decimal

from django.utils import timezone
from rest_framework import status

from api.models import AuditLog, KategoriSampah, Pengaduan, TransaksiSetoran

from .base import EnvelopeAPITestCase


class AuditLogSignalTests(EnvelopeAPITestCase):
    """Verify automatic audit log recording via Django signals."""

    def setUp(self):
        self.admin = self.create_admin(username='admin_audit')
        self.nasabah = self.create_nasabah(username='nasabah_audit')
        self.kategori = KategoriSampah.objects.create(
            nama='PET', harga_beli_per_kg=Decimal('3000.00'),
        )

    def test_create_kategori_logged(self):
        self.auth_as(self.admin)
        response = self.client.post(
            '/api/waste-categories/',
            {'nama': 'Kardus', 'harga_beli_per_kg': '1500.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        log = AuditLog.objects.filter(
            model_name='KategoriSampah', action='create',
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.user_id, self.admin.id)
        self.assertIn('nama', log.changes)

    def test_update_kategori_logged(self):
        self.auth_as(self.admin)
        self.client.patch(
            f'/api/waste-categories/{self.kategori.id}/',
            {'nama': 'Kategori Diperbarui'},
            format='json',
        )

        log = AuditLog.objects.filter(
            model_name='KategoriSampah', action='update',
            object_id=str(self.kategori.id),
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(
            log.changes['nama']['new'], 'Kategori Diperbarui',
        )

    def test_create_pengaduan_logged(self):
        self.auth_as(self.nasabah)
        self.client.post(
            '/api/complaints/',
            {
                'jenis_pengaduan': 'kesalahan_data',
                'keluhan': 'Data saya salah.',
            },
            format='json',
        )

        log = AuditLog.objects.filter(
            model_name='Pengaduan', action='create',
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.user_id, self.nasabah.id)


class AuditLogListTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin(username='admin_audit_list')
        self.koordinator = self.create_koordinator(username='koord_audit')
        self.petugas = self.create_petugas(username='petugas_audit')
        self.nasabah = self.create_nasabah(username='nasabah_audit_list')

        AuditLog.objects.create(
            user=self.admin,
            action='update',
            model_name='TransaksiSetoran',
            object_id='1',
            changes={'total_nilai': {'old': '10000.00', 'new': '10500.00'}},
            ip_address='192.168.1.10',
        )
        AuditLog.objects.create(
            user=self.admin,
            action='create',
            model_name='KategoriSampah',
            object_id='2',
            changes={'nama': {'old': None, 'new': 'PET'}},
        )

    def test_admin_can_list_audit_log(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/audit-log/?model=TransaksiSetoran')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response)
        self.assertEqual(len(response.data['data']), 1)
        self.assertIn('pagination', response.data['meta'])

    def test_koordinator_cannot_access_audit_log(self):
        self.auth_as(self.koordinator)
        response = self.client.get('/api/audit-log/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_petugas_cannot_access_audit_log(self):
        self.auth_as(self.petugas)
        response = self.client.get('/api/audit-log/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_model(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/audit-log/?model=TransaksiSetoran')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['model_name'], 'TransaksiSetoran')

    def test_filter_by_user(self):
        self.auth_as(self.admin)
        response = self.client.get(f'/api/audit-log/?user={self.admin.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)

    def test_filter_by_date_after(self):
        self.auth_as(self.admin)
        today = timezone.localdate().isoformat()
        response = self.client.get(
            f'/api/audit-log/?date_after={today}&model=KategoriSampah',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)


class DepositCorrectionTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin(username='admin_correction')
        self.petugas = self.create_petugas(username='petugas_correction')
        self.koordinator = self.create_koordinator(username='koord_correction')
        self.nasabah = self.create_nasabah(username='nasabah_correction')
        self.kategori = KategoriSampah.objects.create(
            nama='PET', harga_beli_per_kg=Decimal('3000.00'),
        )
        self.nasabah.saldo = Decimal('20250.00')
        self.nasabah.poin = 20
        self.nasabah.save()

        self.deposit = TransaksiSetoran.objects.create(
            nasabah=self.nasabah,
            petugas=self.petugas,
            total_nilai=Decimal('20250.00'),
            status='selesai',
        )
        self.deposit.details.create(
            kategori=self.kategori,
            berat_kg=Decimal('6.75'),
            harga_saat_itu=Decimal('3000.00'),
            subtotal=Decimal('20250.00'),
        )

    def test_admin_can_correct_deposit(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/deposits/{self.deposit.id}/',
            {'total_nilai': '21000.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['total_nilai'], '21000.00')

        self.nasabah.refresh_from_db()
        self.assertEqual(self.nasabah.saldo, Decimal('21000.00'))
        self.assertEqual(self.nasabah.poin, 21)

    def test_correction_creates_audit_log(self):
        self.auth_as(self.admin)
        self.client.patch(
            f'/api/deposits/{self.deposit.id}/',
            {'total_nilai': '19500.00'},
            format='json',
        )

        log = AuditLog.objects.filter(
            model_name='TransaksiSetoran',
            action='update',
            object_id=str(self.deposit.id),
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.user_id, self.admin.id)
        self.assertEqual(log.changes['total_nilai']['old'], '20250.00')
        self.assertEqual(log.changes['total_nilai']['new'], '19500.00')

    def test_petugas_cannot_correct_deposit(self):
        self.auth_as(self.petugas)
        response = self.client.patch(
            f'/api/deposits/{self.deposit.id}/',
            {'total_nilai': '21000.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_koordinator_cannot_correct_deposit(self):
        self.auth_as(self.koordinator)
        response = self.client.patch(
            f'/api/deposits/{self.deposit.id}/',
            {'total_nilai': '21000.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_correction_rejected_if_saldo_insufficient(self):
        self.nasabah.saldo = Decimal('5000.00')
        self.nasabah.save()
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/deposits/{self.deposit.id}/',
            {'total_nilai': '1000.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
