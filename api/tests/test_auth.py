from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import PasswordResetToken
from api.services.whatsapp import create_and_send_otp, get_dev_fixed_otp, verify_otp_code

from .base import EnvelopeAPITestCase

User = get_user_model()


class RegistrationTests(EnvelopeAPITestCase):
    def setUp(self):
        cache.clear()

    def _register_payload(self, **overrides):
        payload = {
            'username': 'budi_baru',
            'password': 'rahasia123',
            'nama_lengkap': 'Budi Baru',
            'setuju_kebijakan_data': True,
        }
        payload.update(overrides)
        return payload

    def test_register_nasabah_success_inactive_until_otp(self):
        response = self.client.post(
            '/api/users/', self._register_payload(), format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assert_envelope_success(response, 201)
        data = response.data['data']
        self.assertEqual(data['username'], 'budi_baru')
        self.assertEqual(data['role'], 'nasabah')
        self.assertEqual(data['saldo'], '0.00')
        self.assertEqual(data['poin'], 0)
        self.assertFalse(data['is_active'])
        self.assertFalse(data['phone_verified'])

        user = User.objects.get(username='budi_baru')
        self.assertEqual(user.role, 'nasabah')
        self.assertFalse(user.is_active)
        self.assertFalse(user.phone_verified)
        self.assertTrue(user.setuju_kebijakan_data)
        self.assertIsNotNone(user.tanggal_persetujuan_kebijakan)

    def test_register_duplicate_username(self):
        self.create_nasabah(username='duplikat')
        response = self.client.post('/api/users/', self._register_payload(
            username='duplikat', nama_lengkap='Duplikat',
        ), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_envelope_error(response, 400)
        self.assertEqual(response.data['code'], 'VALIDATION_ERROR')
        self.assertIn('username', response.data['errors'])

    def test_register_password_too_short(self):
        response = self.client.post('/api/users/', self._register_payload(
            username='pendek', password='12345', nama_lengkap='Password Pendek',
        ), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_envelope_error(response, 400)
        self.assertIn('password', response.data['errors'])

    def test_register_requires_privacy_consent(self):
        response = self.client.post('/api/users/', {
            'username': 'tanpa_consent',
            'password': 'rahasia123',
            'nama_lengkap': 'Tanpa Consent',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('setuju_kebijakan_data', response.data['errors'])

    def test_register_rejects_false_consent(self):
        response = self.client.post('/api/users/', self._register_payload(
            username='false_consent',
            setuju_kebijakan_data=False,
        ), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('setuju_kebijakan_data', response.data['errors'])

    @patch('api.auth_views.create_and_send_otp')
    def test_register_phone_otp_activates_account(self, mock_send):
        def _fake_send(user, purpose, phone, code=None):
            return create_and_send_otp(user, purpose, phone, code='123456')

        mock_send.side_effect = _fake_send

        self.client.post('/api/users/', self._register_payload(), format='json')
        req = self.client.post('/api/auth/phone/request-otp/', {
            'username': 'budi_baru',
            'no_hp': '08122223333',
        }, format='json')
        self.assertEqual(req.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(req, 200)

        verify = self.client.post('/api/auth/phone/verify-otp/', {
            'username': 'budi_baru',
            'otp': '123456',
        }, format='json')
        self.assertEqual(verify.status_code, status.HTTP_200_OK)
        self.assertTrue(verify.data['data']['phone_verified'])
        self.assertTrue(verify.data['data']['is_active'])

        user = User.objects.get(username='budi_baru')
        self.assertTrue(user.is_active)
        self.assertTrue(user.phone_verified)
        self.assertEqual(user.no_hp, '08122223333')

        cache.clear()
        login = self.client.post('/api/auth/login/', {
            'username': 'budi_baru',
            'password': 'rahasia123',
        }, format='json')
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertTrue(login.data['data']['user']['phone_verified'])


class PrivacyPolicyTests(EnvelopeAPITestCase):
    def test_get_privacy_policy_public(self):
        response = self.client.get('/api/privacy-policy/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response)
        data = response.data['data']
        self.assertEqual(data['versi'], '2.0')
        self.assertEqual(data['retensi']['masa_tahun'], 5)
        self.assertIn('penghapusan_akun', data)
        self.assertIn('cara', data['penghapusan_akun'])
        self.assertIn('dipertahankan', data['penghapusan_akun'])
        self.assertIn('hak_pengguna', data)
        self.assertTrue(any('hapus' in hak.lower() for hak in data['hak_pengguna']))
        self.assertIn('data_yang_disimpan', data)
        self.assertIn('keamanan_data_sensitif', data)
        self.assertEqual(
            data['keamanan_data_sensitif']['nik']['status_saat_ini'],
            'tidak_disimpan',
        )
        self.assertNotIn('NIK', ' '.join(
            item for cat in data['data_yang_disimpan']
            for item in cat.get('field', [])
        ))
        self.assertIn('konten', data)
        self.assertIn('#', data['konten'])


class TermsOfServiceTests(EnvelopeAPITestCase):
    def test_get_terms_public(self):
        response = self.client.get('/api/terms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response)
        data = response.data['data']
        self.assertEqual(data['versi'], '1.0')
        self.assertIn('konten', data)
        self.assertIn('Syarat', data['konten'])
        self.assertIn('ringkasan', data)


class LoginTests(EnvelopeAPITestCase):
    def setUp(self):
        cache.clear()
        self.user = self.create_nasabah(username='login_user', password='secret12')

    def test_login_success(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'login_user',
            'password': 'secret12',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        data = response.data['data']
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertEqual(data['user']['role'], 'nasabah')
        self.assertEqual(data['user']['username'], 'login_user')
        self.assertEqual(data['user']['id'], self.user.id)
        self.assertTrue(data['user']['phone_verified'])

    def test_login_wrong_password(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'login_user',
            'password': 'wrongpass',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assert_envelope_error(response, 401)
        self.assertEqual(response.data['code'], 'AUTHENTICATION_FAILED')
        self.assertEqual(response.data['message'], 'Password salah.')
        self.assertIn('password', response.data['errors'])

    def test_login_username_not_found(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'tidak_ada',
            'password': 'secret12',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assert_envelope_error(response, 401)
        self.assertEqual(response.data['message'], 'Username tidak terdaftar.')
        self.assertIn('username', response.data['errors'])

    def test_login_inactive_needs_phone_verify(self):
        self.user.is_active = False
        self.user.phone_verified = False
        self.user.save(update_fields=['is_active', 'phone_verified'])
        response = self.client.post('/api/auth/login/', {
            'username': 'login_user',
            'password': 'secret12',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Verifikasi nomor HP', response.data['message'])


class RefreshTokenTests(EnvelopeAPITestCase):
    def setUp(self):
        cache.clear()
        self.user = self.create_nasabah(username='refresh_user', password='secret12')
        self.refresh = str(RefreshToken.for_user(self.user))

    def test_refresh_token_success(self):
        response = self.client.post('/api/auth/refresh/', {
            'refresh': self.refresh,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        self.assertIn('access', response.data['data'])

    def test_refresh_token_invalid(self):
        response = self.client.post('/api/auth/refresh/', {
            'refresh': 'invalid.token.here',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assert_envelope_error(response, 401)


class MeEndpointTests(EnvelopeAPITestCase):
    def setUp(self):
        cache.clear()
        self.user = self.create_nasabah(username='me_user', password='secret12')
        self.access = self.auth_as(self.user)

    def test_me_get_authenticated(self):
        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        data = response.data['data']
        self.assertEqual(data['username'], 'me_user')
        self.assertEqual(data['role'], 'nasabah')
        self.assertTrue(data['phone_verified'])
        self.assertNotIn('password', data)
        self.assertNotIn('nik', data)
        self.assertNotIn('foto_ktp', data)
        self.assertIn('qr', data)
        self.assertEqual(data['qr'], {
            'id': self.user.id,
            'nama_lengkap': self.user.nama_lengkap,
            'no_hp': self.user.no_hp,
        })

    def test_me_get_unauthenticated(self):
        self.client.credentials()
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assert_envelope_error(response, 401)

    def test_me_patch_profile_phone_unverified(self):
        response = self.client.patch('/api/auth/me/', {
            'nama_lengkap': 'Nama Diperbarui',
            'no_hp': '08999999999',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        self.assertEqual(response.data['data']['nama_lengkap'], 'Nama Diperbarui')
        self.assertFalse(response.data['data']['phone_verified'])

        self.user.refresh_from_db()
        self.assertEqual(self.user.nama_lengkap, 'Nama Diperbarui')
        self.assertFalse(self.user.phone_verified)
        self.assertEqual(response.data['data']['qr']['nama_lengkap'], 'Nama Diperbarui')
        self.assertEqual(response.data['data']['qr']['no_hp'], '08999999999')

    def test_me_patch_username(self):
        other = self.create_nasabah(username='taken_user')
        taken = self.client.patch('/api/auth/me/', {
            'username': other.username,
        }, format='json')
        self.assertEqual(taken.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', taken.data['errors'])

        response = self.client.patch('/api/auth/me/', {
            'username': 'me_user_baru',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['username'], 'me_user_baru')
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'me_user_baru')

    def test_me_patch_cannot_change_role(self):
        response = self.client.patch('/api/auth/me/', {
            'role': 'admin',
            'saldo': '999999.00',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'nasabah')
        self.assertEqual(self.user.saldo, 0)
        self.assertEqual(self.user.poin, 0)


class ForgotPasswordOtpTests(EnvelopeAPITestCase):
    def setUp(self):
        cache.clear()
        self.user = self.create_nasabah(username='reset_user', password='secret12')

    def test_forgot_password_unknown_username_no_orphan_token(self):
        before = PasswordResetToken.objects.count()
        response = self.client.post('/api/auth/forgot-password/', {
            'username': 'ghost_user',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Username tidak terdaftar.')
        self.assertEqual(PasswordResetToken.objects.count(), before)

    def test_forgot_password_known_username_returns_masked_phone(self):
        response = self.client.post('/api/auth/forgot-password/', {
            'username': 'reset_user',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        self.assertEqual(response.data['data']['next'], 'confirm_phone')
        self.assertIn('masked_phone', response.data['data'])
        self.assertEqual(PasswordResetToken.objects.count(), 0)

    @patch('api.auth_views.create_and_send_otp')
    def test_reset_password_otp_full_flow(self, mock_send):
        def _fake_send(user, purpose, phone, code=None):
            return create_and_send_otp(user, purpose, phone, code='654321')

        mock_send.side_effect = _fake_send

        mismatch = self.client.post('/api/auth/reset-password/request-otp/', {
            'username': 'reset_user',
            'no_hp': '08999999999',
        }, format='json')
        self.assertEqual(mismatch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('no_hp', mismatch.data['errors'])

        req = self.client.post('/api/auth/reset-password/request-otp/', {
            'username': 'reset_user',
            'no_hp': '08123456789',
        }, format='json')
        self.assertEqual(req.status_code, status.HTTP_200_OK)

        verify = self.client.post('/api/auth/reset-password/verify-otp/', {
            'username': 'reset_user',
            'otp': '654321',
        }, format='json')
        self.assertEqual(verify.status_code, status.HTTP_200_OK)
        reset_token = verify.data['data']['reset_token']
        self.assertTrue(PasswordResetToken.objects.filter(token=reset_token).exists())

        bad_confirm = self.client.post('/api/auth/reset-password/', {
            'token': reset_token,
            'password': 'baru1234',
            'password_confirm': 'beda1234',
        }, format='json')
        self.assertEqual(bad_confirm.status_code, status.HTTP_400_BAD_REQUEST)

        ok = self.client.post('/api/auth/reset-password/', {
            'token': reset_token,
            'password': 'baru1234',
            'password_confirm': 'baru1234',
        }, format='json')
        self.assertEqual(ok.status_code, status.HTTP_200_OK)

        cache.clear()
        login = self.client.post('/api/auth/login/', {
            'username': 'reset_user',
            'password': 'baru1234',
        }, format='json')
        self.assertEqual(login.status_code, status.HTTP_200_OK)


class AdminPhoneVerifiedTests(EnvelopeAPITestCase):
    """T10 — admin create/update set phone_verified=false saat nomor diisi/diubah."""

    def setUp(self):
        cache.clear()
        self.admin = self.create_admin()
        self.auth_as(self.admin)

    def test_admin_create_staff_with_phone_unverified(self):
        response = self.client.post('/api/users/', {
            'username': 'petugas_baru',
            'password': 'secret12',
            'nama_lengkap': 'Petugas Baru',
            'role': 'petugas',
            'no_hp': '08120001111',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['data']['phone_verified'])
        user = User.objects.get(username='petugas_baru')
        self.assertFalse(user.phone_verified)

    def test_admin_update_phone_resets_verified(self):
        petugas = self.create_petugas(username='petugas_hp')
        petugas.phone_verified = True
        petugas.save(update_fields=['phone_verified'])

        response = self.client.patch(f'/api/users/{petugas.id}/', {
            'no_hp': '08129998888',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['data']['phone_verified'])
        petugas.refresh_from_db()
        self.assertFalse(petugas.phone_verified)
        self.assertEqual(petugas.no_hp, '08129998888')


@override_settings(DEBUG=True, OTP_DEV_FIXED_CODE='123456')
class OtpDevFixedCodeTests(EnvelopeAPITestCase):
    """OTP tetap untuk local/dev — lihat docs/OTP_DEV.md."""

    def setUp(self):
        cache.clear()
        self.user = self.create_nasabah(username='otp_dev_user', password='secret12')
        self.user.phone_verified = False
        self.user.save(update_fields=['phone_verified'])

    def test_get_dev_fixed_otp_when_debug(self):
        self.assertEqual(get_dev_fixed_otp(), '123456')

    @override_settings(DEBUG=False, OTP_DEV_FIXED_CODE='123456')
    def test_dev_otp_ignored_when_not_debug(self):
        self.assertIsNone(get_dev_fixed_otp())

    @override_settings(DEBUG=True, OTP_DEV_FIXED_CODE='12ab')
    def test_invalid_dev_code_ignored(self):
        self.assertIsNone(get_dev_fixed_otp())

    def test_phone_request_otp_returns_dev_fields_and_accepts_fixed_code(self):
        self.auth_as(self.user)
        req = self.client.post('/api/auth/phone/request-otp/', {
            'no_hp': '08123456789',
        }, format='json')
        self.assertEqual(req.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(req, 200)
        self.assertTrue(req.data['data']['dev_otp_mode'])
        self.assertEqual(req.data['data']['dev_otp'], '123456')
        self.assertIn('123456', req.data['message'])

        verify = self.client.post('/api/auth/phone/verify-otp/', {
            'otp': '123456',
        }, format='json')
        self.assertEqual(verify.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.phone_verified)

    def test_reset_password_request_otp_dev_mode(self):
        req = self.client.post('/api/auth/reset-password/request-otp/', {
            'username': 'otp_dev_user',
            'no_hp': '08123456789',
        }, format='json')
        self.assertEqual(req.status_code, status.HTTP_200_OK)
        self.assertEqual(req.data['data']['dev_otp'], '123456')
        verify_otp_code(self.user, 'password_reset', '123456')


class AddressGateTests(EnvelopeAPITestCase):
    def setUp(self):
        cache.clear()
        self.nasabah = self.create_nasabah(username='gate_user')
        self.nasabah.alamat = ''
        self.nasabah.save(update_fields=['alamat'])
        self.auth_as(self.nasabah)

    def test_pickup_blocked_without_address(self):
        from django.utils import timezone
        from datetime import timedelta
        response = self.client.post('/api/pickups/', {
            'estimasi_berat': '10.00',
            'alamat_jemput': 'Jl. Test',
            'jadwal': (timezone.now() + timedelta(days=2)).isoformat(),
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('alamat', response.data['errors'])
        self.assertIn('Lengkapi alamat', response.data['errors']['alamat'][0])

    def test_withdrawal_blocked_without_address(self):
        self.nasabah.saldo = 100000
        self.nasabah.save(update_fields=['saldo'])
        response = self.client.post('/api/withdrawals/', {
            'nominal': '50000.00',
            'metode': 'tunai',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('alamat', response.data['errors'])

    def test_redemption_blocked_without_address(self):
        from api.models import Reward
        reward = Reward.objects.create(
            nama='Voucher', poin_dibutuhkan=10, stok=5,
        )
        self.nasabah.poin = 100
        self.nasabah.save(update_fields=['poin'])
        response = self.client.post('/api/reward-redemptions/', {
            'reward': reward.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('alamat', response.data['errors'])
