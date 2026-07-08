from decimal import Decimal

from rest_framework import status

from api.models import PenarikanSaldo

from .base import EnvelopeAPITestCase


class WithdrawalCreateTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah(username='nasabah_wd')
        self.nasabah.saldo = Decimal('200000.00')
        self.nasabah.save()
        self.admin = self.create_admin(username='admin_wd')
        self.koordinator = self.create_koordinator(username='koord_wd')

    def _payload(self, **overrides):
        payload = {'nominal': '100000.00', 'metode': 'tunai'}
        payload.update(overrides)
        return payload

    def test_nasabah_create_success(self):
        self.auth_as(self.nasabah)
        response = self.client.post('/api/withdrawals/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data['data']
        self.assertEqual(data['status'], 'menunggu')
        self.assertEqual(data['nominal'], '100000.00')
        self.assertEqual(data['nasabah'], self.nasabah.id)

    def test_reject_nominal_below_minimum(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/withdrawals/', self._payload(nominal='30000.00'), format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_insufficient_saldo(self):
        self.nasabah.saldo = Decimal('40000.00')
        self.nasabah.save()
        self.auth_as(self.nasabah)
        response = self.client.post('/api/withdrawals/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_duplicate_pending(self):
        PenarikanSaldo.objects.create(
            nasabah=self.nasabah,
            nominal=Decimal('50000.00'),
            metode='tunai',
            status='menunggu',
        )
        self.auth_as(self.nasabah)
        response = self.client.post('/api/withdrawals/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_cannot_create(self):
        self.auth_as(self.admin)
        response = self.client.post('/api/withdrawals/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class WithdrawalApproveTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah(username='nasabah_wd2')
        self.nasabah.saldo = Decimal('200000.00')
        self.nasabah.save()
        self.admin = self.create_admin(username='admin_wd2')
        self.koordinator = self.create_koordinator(username='koord_wd2')
        self.withdrawal = PenarikanSaldo.objects.create(
            nasabah=self.nasabah,
            nominal=Decimal('100000.00'),
            metode='tunai',
            status='menunggu',
        )

    def test_admin_approve_debits_saldo(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/withdrawals/{self.withdrawal.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'selesai')
        self.assertEqual(response.data['data']['saldo_nasabah_baru'], '100000.00')
        self.nasabah.refresh_from_db()
        self.assertEqual(self.nasabah.saldo, Decimal('100000.00'))

    def test_koordinator_can_approve(self):
        self.auth_as(self.koordinator)
        response = self.client.patch(
            f'/api/withdrawals/{self.withdrawal.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nasabah_cannot_approve(self):
        self.auth_as(self.nasabah)
        response = self.client.patch(
            f'/api/withdrawals/{self.withdrawal.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_prevent_double_processing(self):
        self.withdrawal.status = 'selesai'
        self.withdrawal.save()
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/withdrawals/{self.withdrawal.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_approve_rejects_insufficient_saldo(self):
        self.nasabah.saldo = Decimal('50000.00')
        self.nasabah.save()
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/withdrawals/{self.withdrawal.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.nasabah.refresh_from_db()
        self.assertEqual(self.nasabah.saldo, Decimal('50000.00'))

    def test_filter_by_status(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/withdrawals/?status=menunggu')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_nasabah_only_sees_own(self):
        other = self.create_nasabah(username='nasabah_other_wd')
        PenarikanSaldo.objects.create(
            nasabah=other,
            nominal=Decimal('50000.00'),
            metode='tunai',
            status='menunggu',
        )
        self.auth_as(self.nasabah)
        response = self.client.get('/api/withdrawals/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['nasabah'], self.nasabah.id)
