import re
from datetime import timedelta
from io import StringIO

from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from rest_framework import status

from api.models import User

from .base import EnvelopeAPITestCase


def _otp_from_outbox() -> str:
    return re.search(r'Kode OTP Anda: (\d{6})', mail.outbox[-1].body).group(1)


class EmailOtpTestCase(EnvelopeAPITestCase):
    def setUp(self):
        cache.clear()
        mail.outbox = []

    def _register(self, username='warga_baru', password='secret12'):
        response = self.client.post('/api/users/', {
            'username': username,
            'password': password,
            'nama_lengkap': 'Warga Baru',
            'setuju_kebijakan_data': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return User.objects.get(username=username)

    def _request(self, **data):
        return self.client.post('/api/auth/email/request-otp/', data, format='json')

    def _verify(self, **data):
        return self.client.post('/api/auth/email/verify-otp/', data, format='json')


class RegistrationEmailOtpTests(EmailOtpTestCase):
    def test_full_registration_flow_activates_account(self):
        user = self._register()
        self.assertFalse(user.is_active)

        response = self._request(username='warga_baru', password='secret12', email='Warga@Gmail.com')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['masked_email'], 'wa***@gmail.com')
        self.assertEqual(response.data['data']['purpose'], 'registration')
        self.assertEqual(mail.outbox[-1].to, ['warga@gmail.com'])

        response = self._verify(username='warga_baru', otp=_otp_from_outbox())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.email_verified)
        self.assertEqual(user.email, 'warga@gmail.com')

        login = self.client.post('/api/auth/login/', {
            'username': 'warga_baru', 'password': 'secret12',
        }, format='json')
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertFalse(login.data['data']['user']['email_required'])

    def test_wrong_otp_keeps_account_inactive(self):
        user = self._register()
        self._request(username='warga_baru', password='secret12', email='warga@gmail.com')
        response = self._verify(username='warga_baru', otp='000000')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_request_requires_correct_password(self):
        self._register()
        response = self._request(username='warga_baru', password='salah999', email='warga@gmail.com')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self._request(username='warga_baru', email='warga@gmail.com')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(mail.outbox, [])

    def test_disposable_email_rejected(self):
        self._register()
        response = self._request(username='warga_baru', password='secret12', email='bot@mailinator.com')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])

    def test_email_verified_by_other_account_rejected(self):
        other = self.create_nasabah(username='pemilik_email')
        other.email = 'dipakai@gmail.com'
        other.email_verified = True
        other.save()
        self._register()
        response = self._request(username='warga_baru', password='secret12', email='DIPAKAI@gmail.com')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_per_email_hourly_cap(self):
        for i in range(3):
            self._register(username=f'bot_{i}')
            ok = self._request(username=f'bot_{i}', password='secret12', email='korban@gmail.com')
            self.assertEqual(ok.status_code, status.HTTP_200_OK)
        self._register(username='bot_3')
        response = self._request(username='bot_3', password='secret12', email='korban@gmail.com')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 3)

    def test_deactivated_account_cannot_reactivate_via_email(self):
        user = self.create_nasabah(username='diblokir')
        user.is_active = False
        user.last_login = timezone.now()
        user.save()
        response = self._request(username='diblokir', password='secret12', email='blok@gmail.com')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(SKIP_OTP_VERIFICATION=True)
    def test_skip_mode_verifies_without_otp(self):
        user = self._register()
        response = self._request(username='warga_baru', password='secret12', email='warga@gmail.com')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active and user.email_verified)
        self.assertEqual(mail.outbox, [])

    def test_registration_throttled_per_ip_per_day(self):
        codes = [
            self.client.post('/api/users/', {
                'username': f'massal_{i}', 'password': 'secret12',
                'nama_lengkap': 'Bot', 'setuju_kebijakan_data': True,
            }, format='json').status_code
            for i in range(11)
        ]
        self.assertEqual(codes[:10], [201] * 10)
        self.assertEqual(codes[10], status.HTTP_429_TOO_MANY_REQUESTS)


class LoggedInEmailVerificationTests(EmailOtpTestCase):
    def test_staff_without_email_must_verify_then_cleared(self):
        petugas = self.create_petugas()
        login = self.client.post('/api/auth/login/', {
            'username': 'petugas_test', 'password': 'secret12',
        }, format='json')
        self.assertTrue(login.data['data']['user']['email_required'])

        self.auth_as(petugas)
        response = self._request(email='petugas@gmail.com')
        self.assertEqual(response.data['data']['purpose'], 'email_verify')
        response = self._verify(otp=_otp_from_outbox())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['data']['user']['email_required'])
        self.assertEqual(response.data['data']['user']['email'], 'petugas@gmail.com')

    def test_email_saved_only_after_otp(self):
        nasabah = self.create_nasabah()
        self.auth_as(nasabah)
        self._request(email='baru@gmail.com')
        nasabah.refresh_from_db()
        self.assertEqual(nasabah.email, '')
        self.assertFalse(nasabah.email_verified)

    def test_profile_patch_cannot_set_email(self):
        nasabah = self.create_nasabah()
        self.auth_as(nasabah)
        self.client.patch('/api/auth/me/', {'email': 'curang@gmail.com'}, format='json')
        nasabah.refresh_from_db()
        self.assertEqual(nasabah.email, '')

    def test_admin_created_nasabah_without_email_is_exempt(self):
        self.auth_as(self.create_admin())
        response = self.client.post('/api/users/', {
            'username': 'dibantu_admin', 'password': 'secret12', 'role': 'nasabah',
            'nama_lengkap': 'Warga Lansia', 'setuju_kebijakan_data': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['data']['email_required'])

        response = self.client.post('/api/users/', {
            'username': 'petugas_baru', 'password': 'secret12', 'role': 'petugas',
            'nama_lengkap': 'Petugas Baru',
        }, format='json')
        self.assertTrue(response.data['data']['email_required'])


class PasswordResetEmailTests(EmailOtpTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_nasabah(username='lupa_sandi')
        self.user.email = 'lupa@gmail.com'
        self.user.email_verified = True
        self.user.save()

    def test_full_reset_flow(self):
        response = self.client.post('/api/auth/forgot-password/', {'username': 'lupa_sandi'}, format='json')
        self.assertEqual(response.data['data']['next'], 'confirm_email')
        self.assertEqual(response.data['data']['masked_email'], 'lu***@gmail.com')

        response = self.client.post('/api/auth/reset-password/request-otp/', {
            'username': 'lupa_sandi', 'email': 'LUPA@gmail.com',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post('/api/auth/reset-password/verify-otp/', {
            'username': 'lupa_sandi', 'otp': _otp_from_outbox(),
        }, format='json')
        token = response.data['data']['reset_token']
        response = self.client.post('/api/auth/reset-password/', {
            'token': token, 'password': 'barubaru1', 'password_confirm': 'barubaru1',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('barubaru1'))

    def test_wrong_email_rejected(self):
        response = self.client.post('/api/auth/reset-password/request-otp/', {
            'username': 'lupa_sandi', 'email': 'orang@lain.com',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(mail.outbox, [])

    def test_no_verified_email_tells_to_contact_admin(self):
        self.create_nasabah(username='tanpa_email')
        response = self.client.post('/api/auth/forgot-password/', {'username': 'tanpa_email'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Hubungi admin', response.data['message'])


class DeleteAccountEmailTests(EmailOtpTestCase):
    def test_delete_account_via_email(self):
        user = self.create_nasabah(username='hapus_email')
        user.email = 'hapus@gmail.com'
        user.email_verified = True
        user.save()

        check = self.client.post('/api/auth/delete-account/check/', {'username': 'hapus_email'}, format='json')
        self.assertEqual(check.data['data']['next'], 'confirm_email')

        req = self.client.post('/api/auth/delete-account/request-otp/', {
            'username': 'hapus_email', 'email': 'hapus@gmail.com',
        }, format='json')
        self.assertEqual(req.status_code, status.HTTP_200_OK)
        self.assertEqual(req.data['data']['masked_email'], 'ha***@gmail.com')

        confirm = self.client.post('/api/auth/delete-account/confirm/', {
            'username': 'hapus_email', 'otp': _otp_from_outbox(),
            'confirmation_text': 'hapus_email', 'acknowledge': True,
        }, format='json')
        self.assertEqual(confirm.status_code, status.HTTP_200_OK)


class WhatsappDisabledTests(EmailOtpTestCase):
    def test_phone_otp_endpoints_disabled(self):
        for path in ('/api/auth/phone/request-otp/', '/api/auth/phone/verify-otp/'):
            response = self.client.post(path, {'username': 'x', 'no_hp': '0812', 'otp': '1'}, format='json')
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(response.data['code'], 'OTP_CHANNEL_DISABLED')


class CleanupUnverifiedTests(EmailOtpTestCase):
    def test_cleanup_deletes_only_old_pending_registrations(self):
        old = self._register(username='lama_pending')
        User.objects.filter(pk=old.pk).update(date_joined=timezone.now() - timedelta(hours=30))
        self._register(username='baru_pending')
        disabled = self.create_nasabah(username='dinonaktifkan')
        User.objects.filter(pk=disabled.pk).update(
            is_active=False, last_login=timezone.now(),
            date_joined=timezone.now() - timedelta(days=10),
        )

        call_command('cleanup_unverified_accounts', stdout=StringIO())
        remaining = set(User.objects.values_list('username', flat=True))
        self.assertNotIn('lama_pending', remaining)
        self.assertIn('baru_pending', remaining)
        self.assertIn('dinonaktifkan', remaining)
