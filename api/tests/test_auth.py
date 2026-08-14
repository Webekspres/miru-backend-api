from django.contrib.auth import get_user_model
from rest_framework import status

from .base import EnvelopeAPITestCase

User = get_user_model()


class RegistrationTests(EnvelopeAPITestCase):
    def _register_payload(self, **overrides):
        payload = {
            'username': 'budi_baru',
            'password': 'rahasia123',
            'nama_lengkap': 'Budi Baru',
            'no_hp': '08111111111',
            'alamat': 'Timika',
            'setuju_kebijakan_data': True,
        }
        payload.update(overrides)
        return payload

    def test_register_nasabah_success(self):
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

        user = User.objects.get(username='budi_baru')
        self.assertEqual(user.role, 'nasabah')
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


class PrivacyPolicyTests(EnvelopeAPITestCase):
    def test_get_privacy_policy_public(self):
        response = self.client.get('/api/privacy-policy/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response)
        data = response.data['data']
        self.assertEqual(data['versi'], '1.0')
        self.assertEqual(data['retensi']['masa_tahun'], 5)
        self.assertIn('data_yang_disimpan', data)
        self.assertIn('keamanan_data_sensitif', data)
        self.assertIn('status_saat_ini', data['keamanan_data_sensitif']['nik'])


class LoginTests(EnvelopeAPITestCase):
    def setUp(self):
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

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'login_user',
            'password': 'wrongpass',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assert_envelope_error(response, 401)
        self.assertEqual(response.data['code'], 'AUTHENTICATION_FAILED')


class RefreshTokenTests(EnvelopeAPITestCase):
    def setUp(self):
        self.create_nasabah(username='refresh_user', password='secret12')
        login = self.client.post('/api/auth/login/', {
            'username': 'refresh_user',
            'password': 'secret12',
        }, format='json')
        self.refresh = login.data['data']['refresh']

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
        self.user = self.create_nasabah(username='me_user', password='secret12')
        login = self.client.post('/api/auth/login/', {
            'username': 'me_user',
            'password': 'secret12',
        }, format='json')
        self.access = login.data['data']['access']

    def test_me_get_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        data = response.data['data']
        self.assertEqual(data['username'], 'me_user')
        self.assertEqual(data['role'], 'nasabah')
        self.assertNotIn('password', data)
        self.assertIn('qr', data)
        self.assertEqual(data['qr'], {
            'id': self.user.id,
            'nama_lengkap': self.user.nama_lengkap,
            'no_hp': self.user.no_hp,
        })

    def test_me_get_unauthenticated(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assert_envelope_error(response, 401)

    def test_me_patch_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        response = self.client.patch('/api/auth/me/', {
            'nama_lengkap': 'Nama Diperbarui',
            'no_hp': '08999999999',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        self.assertEqual(response.data['data']['nama_lengkap'], 'Nama Diperbarui')

        self.user.refresh_from_db()
        self.assertEqual(self.user.nama_lengkap, 'Nama Diperbarui')
        self.assertEqual(response.data['data']['qr']['nama_lengkap'], 'Nama Diperbarui')
        self.assertEqual(response.data['data']['qr']['no_hp'], '08999999999')

    def test_me_patch_cannot_change_role(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        response = self.client.patch('/api/auth/me/', {
            'role': 'admin',
            'saldo': '999999.00',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'nasabah')
        self.assertEqual(self.user.saldo, 0)
        self.assertEqual(self.user.poin, 0)
