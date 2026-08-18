from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status

from api.models import (
    DeviceToken,
    Notifikasi,
    PasswordResetToken,
    PhoneOTP,
    TransaksiSetoran,
)
from api.services.whatsapp import create_and_send_otp

from .base import EnvelopeAPITestCase

User = get_user_model()


class DeleteAccountTests(EnvelopeAPITestCase):
    def setUp(self):
        cache.clear()
        self.user = self.create_nasabah(username='hapus_akun', password='secret12')
        self.user.saldo = 50000
        self.user.poin = 30
        self.user.save(update_fields=['saldo', 'poin'])
        self.transaksi = TransaksiSetoran.objects.create(
            nasabah=self.user, total_nilai='10000.00',
        )

    def _check(self, username='hapus_akun'):
        return self.client.post(
            '/api/auth/delete-account/check/',
            {'username': username},
            format='json',
        )

    def _request_otp(self, username='hapus_akun', no_hp='08123456789'):
        return self.client.post(
            '/api/auth/delete-account/request-otp/',
            {'username': username, 'no_hp': no_hp},
            format='json',
        )

    def _confirm(self, **overrides):
        payload = {
            'username': 'hapus_akun',
            'otp': '123456',
            'confirmation_text': 'hapus_akun',
            'acknowledge': True,
        }
        payload.update(overrides)
        return self.client.post(
            '/api/auth/delete-account/confirm/',
            payload,
            format='json',
        )

    @patch('api.delete_account_views.create_and_send_otp')
    def _send_otp(self, mock_send, username='hapus_akun'):
        def _fake_send(user, purpose, phone, code=None):
            return create_and_send_otp(user, purpose, phone, code='123456')

        mock_send.side_effect = _fake_send
        return self._request_otp(username=username)

    # ── Langkah 1: check ──────────────────────────────────────────────

    def test_check_unknown_username_404(self):
        response = self._check('ghost_user')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assert_envelope_error(response, 404)

    def test_check_requires_username(self):
        response = self._check('')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data['errors'])

    def test_check_staff_role_rejected(self):
        petugas = self.create_petugas(username='petugas_hapus')
        response = self._check(petugas.username)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'VALIDATION_ERROR')
        self.assertIn('username', response.data['errors'])

    def test_check_success_returns_summary(self):
        response = self._check()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        data = response.data['data']
        self.assertEqual(data['username'], 'hapus_akun')
        self.assertEqual(data['nama_lengkap'], 'Nasabah Test')
        self.assertEqual(data['masked_phone'], '081****89')
        self.assertEqual(data['saldo'], '50000.00')
        self.assertEqual(data['poin'], 30)
        self.assertEqual(data['riwayat']['jumlah_setoran'], 1)
        self.assertEqual(data['riwayat']['jumlah_penjemputan'], 0)
        self.assertEqual(data['next'], 'confirm_phone')
        self.assertNotIn('no_hp', data)

    # ── Langkah 2: request OTP ────────────────────────────────────────

    def test_request_otp_wrong_phone_400(self):
        response = self._request_otp(no_hp='08999999999')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('no_hp', response.data['errors'])

    def test_request_otp_success_uses_account_deletion_purpose(self):
        response = self._send_otp()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        self.assertEqual(response.data['data']['masked_phone'], '081****89')

        otp = PhoneOTP.objects.filter(
            user=self.user, purpose=PhoneOTP.PURPOSE_ACCOUNT_DELETION,
        ).first()
        self.assertIsNotNone(otp)
        self.assertFalse(otp.is_used)

    # ── Langkah 3: confirm ────────────────────────────────────────────

    def test_confirm_requires_acknowledge(self):
        self._send_otp()
        response = self._confirm(acknowledge=False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('acknowledge', response.data['errors'])

    def test_confirm_requires_confirmation_text(self):
        self._send_otp()
        response = self._confirm(confirmation_text='')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirmation_text', response.data['errors'])

    def test_confirm_wrong_confirmation_text_rejected(self):
        self._send_otp()
        response = self._confirm(confirmation_text='tidakpaham')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirmation_text', response.data['errors'])
        # Akun tetap utuh
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_confirm_accepts_phrase_hapus_akun(self):
        self._send_otp()
        response = self._confirm(confirmation_text='hapus akun')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_confirm_wrong_otp_rejected(self):
        self._send_otp()
        response = self._confirm(otp='000000')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('otp', response.data['errors'])

    def test_confirm_full_flow_anonymizes_and_deactivates(self):
        Notifikasi.objects.create(
            user=self.user, judul='Test', deskripsi='x', kategori='sistem',
        )
        DeviceToken.objects.create(
            user=self.user, token='fcm-token-1', platform='android',
        )
        PasswordResetToken.objects.create(user=self.user, token='reset-xyz')
        self.auth_as(self.user)  # pastikan ada sesi aktif sebelum hapus

        response = self._send_otp()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        confirm = self._confirm()
        self.assertEqual(confirm.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(confirm, 200)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertEqual(self.user.username, f'deleted_{self.user.pk}')
        self.assertEqual(self.user.nama_lengkap, 'Akun Terhapus')
        self.assertEqual(self.user.no_hp, '')
        self.assertEqual(self.user.email, '')
        self.assertEqual(self.user.alamat, '')
        self.assertFalse(self.user.phone_verified)
        self.assertEqual(self.user.saldo, 0)
        self.assertEqual(self.user.poin, 0)
        self.assertFalse(self.user.has_usable_password())

        # Data sesi & notifikasi dibersihkan
        self.assertEqual(Notifikasi.objects.filter(user=self.user).count(), 0)
        self.assertEqual(DeviceToken.objects.filter(user=self.user).count(), 0)
        self.assertEqual(PasswordResetToken.objects.filter(user=self.user).count(), 0)
        self.assertEqual(
            PhoneOTP.objects.filter(user=self.user).count(), 0,
        )

        # Catatan transaksi dipertahankan (catatan keuangan bank sampah)
        self.assertTrue(
            TransaksiSetoran.objects.filter(pk=self.transaksi.pk).exists(),
        )

        # Login tidak bisa lagi
        cache.clear()
        login = self.client.post('/api/auth/login/', {
            'username': 'hapus_akun',
            'password': 'secret12',
        }, format='json')
        self.assertEqual(login.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_confirm_twice_not_found(self):
        self._send_otp()
        self.assertEqual(self._confirm().status_code, status.HTTP_200_OK)

        # Username lama sudah tidak ditemukan untuk alur hapus akun
        response = self._check()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self._request_otp()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
