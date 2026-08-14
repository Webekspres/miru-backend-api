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
        payload = {
            'nominal': '100000.00',
            'metode': 'tunai',
            'nama_bank': '',
            'no_rekening': '',
            'nama_pemilik_rekening': '',
        }
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
        self.assertIn('1–2 hari kerja', response.data['message'])

    def test_reject_nominal_below_minimum(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/withdrawals/', self._payload(nominal='30000.00'), format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nominal', response.data['errors'])
        self.assertIn('minimal', response.data['message'].lower())

    def test_reject_insufficient_saldo(self):
        self.nasabah.saldo = Decimal('40000.00')
        self.nasabah.save()
        self.auth_as(self.nasabah)
        response = self.client.post('/api/withdrawals/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nominal', response.data['errors'])
        self.assertIn('tidak mencukupi', response.data['message'].lower())

    def test_reject_invalid_metode(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/withdrawals/', self._payload(metode='crypto'), format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('metode', response.data['errors'])

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
        self.assertIn('nominal', response.data['errors'])

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


class WithdrawalActionTests(EnvelopeAPITestCase):
    """SOP A.3 — action endpoints approve/reject."""

    def setUp(self):
        self.nasabah = self.create_nasabah(username='nasabah_wd3')
        self.nasabah.saldo = Decimal('200000.00')
        self.nasabah.save()
        self.admin = self.create_admin(username='admin_wd3')
        self.koordinator = self.create_koordinator(username='koord_wd3')
        self.withdrawal = PenarikanSaldo.objects.create(
            nasabah=self.nasabah,
            nominal=Decimal('100000.00'),
            metode='tunai',
            status='menunggu',
        )

    def test_approve_action_debits_saldo(self):
        self.auth_as(self.admin)
        response = self.client.post(
            f'/api/withdrawals/{self.withdrawal.id}/approve/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'selesai')
        self.assertEqual(response.data['data']['saldo_nasabah_baru'], '100000.00')
        self.nasabah.refresh_from_db()
        self.assertEqual(self.nasabah.saldo, Decimal('100000.00'))

    def test_koordinator_can_approve_action(self):
        self.auth_as(self.koordinator)
        response = self.client.post(
            f'/api/withdrawals/{self.withdrawal.id}/approve/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reject_action_no_saldo_change(self):
        saldo_before = self.nasabah.saldo
        self.auth_as(self.admin)
        response = self.client.post(
            f'/api/withdrawals/{self.withdrawal.id}/reject/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'ditolak')
        self.nasabah.refresh_from_db()
        self.assertEqual(self.nasabah.saldo, saldo_before)

    def test_nasabah_cannot_approve_action(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            f'/api/withdrawals/{self.withdrawal.id}/approve/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_double_approve_returns_409(self):
        self.auth_as(self.admin)
        self.client.post(f'/api/withdrawals/{self.withdrawal.id}/approve/')
        response = self.client.post(
            f'/api/withdrawals/{self.withdrawal.id}/approve/',
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_e2e_create_approve_flow(self):
        fresh = self.create_nasabah(username='nasabah_wd_e2e')
        fresh.saldo = Decimal('200000.00')
        fresh.save()
        self.auth_as(fresh)
        create = self.client.post('/api/withdrawals/', {
            'nominal': '75000.00', 'metode': 'transfer',
        }, format='json')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertIn('1–2 hari kerja', create.data['message'])
        wd_id = create.data['data']['id']

        self.auth_as(self.admin)
        approve = self.client.post(f'/api/withdrawals/{wd_id}/approve/')
        self.assertEqual(approve.status_code, status.HTTP_200_OK)
        fresh.refresh_from_db()
        self.assertEqual(fresh.saldo, Decimal('125000.00'))


class WithdrawalKtpLampiranTests(EnvelopeAPITestCase):
    """PDP: KTP hanya lampiran sementara penarikan ≥ 1 juta."""

    PNG = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
        b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
        b'\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    def setUp(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.nasabah = self.create_nasabah(username='nasabah_ktp')
        self.nasabah.saldo = Decimal('2000000.00')
        self.nasabah.save()
        self.admin = self.create_admin(username='admin_ktp')
        self._png = lambda: SimpleUploadedFile(
            'ktp.png', self.PNG, content_type='image/png',
        )

    def test_profile_has_no_nik_or_foto_ktp(self):
        self.auth_as(self.nasabah)
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertNotIn('nik', data)
        self.assertNotIn('foto_ktp', data)

    def test_besar_tanpa_lampiran_ditolak(self):
        self.auth_as(self.nasabah)
        response = self.client.post('/api/withdrawals/', {
            'nominal': '1000000.00',
            'metode': 'tunai',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('lampiran_ktp', response.data['errors'])

    def test_besar_dengan_lampiran_lalu_dihapus_saat_approve(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/withdrawals/',
            {
                'nominal': '1000000.00',
                'metode': 'tunai',
                'lampiran_ktp': self._png(),
            },
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data['data']
        self.assertTrue(data['ada_lampiran_ktp'])
        self.assertNotIn('lampiran_ktp', data)
        wd_id = data['id']

        self.auth_as(self.admin)
        download = self.client.get(f'/api/withdrawals/{wd_id}/lampiran-ktp/')
        self.assertEqual(download.status_code, status.HTTP_200_OK)

        self.auth_as(self.nasabah)
        forbidden = self.client.get(f'/api/withdrawals/{wd_id}/lampiran-ktp/')
        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)

        self.auth_as(self.admin)
        approve = self.client.post(f'/api/withdrawals/{wd_id}/approve/')
        self.assertEqual(approve.status_code, status.HTTP_200_OK)
        self.assertFalse(approve.data['data']['ada_lampiran_ktp'])
        self.assertTrue(approve.data['data']['ktp_diverifikasi'])

        gone = self.client.get(f'/api/withdrawals/{wd_id}/lampiran-ktp/')
        self.assertEqual(gone.status_code, status.HTTP_404_NOT_FOUND)

        wd = PenarikanSaldo.objects.get(pk=wd_id)
        self.assertFalse(wd.lampiran_ktp)
        self.assertTrue(wd.ktp_diverifikasi)
