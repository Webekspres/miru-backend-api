from django.contrib.auth import get_user_model
from rest_framework import status

from .base import EnvelopeAPITestCase

User = get_user_model()


class RegistrationTests(EnvelopeAPITestCase):
    def test_register_nasabah_success(self):
        response = self.client.post('/api/users/', {
            'username': 'budi_baru',
            'password': 'rahasia123',
            'nama_lengkap': 'Budi Baru',
            'no_hp': '08111111111',
            'alamat': 'Timika',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assert_envelope_success(response, 201)
        data = response.data['data']
        self.assertEqual(data['username'], 'budi_baru')
        self.assertEqual(data['role'], 'nasabah')
        self.assertEqual(data['saldo'], '0.00')
        self.assertEqual(data['poin'], 0)

        user = User.objects.get(username='budi_baru')
        self.assertEqual(user.role, 'nasabah')

    def test_register_duplicate_username(self):
        self.create_nasabah(username='duplikat')
        response = self.client.post('/api/users/', {
            'username': 'duplikat',
            'password': 'rahasia123',
            'nama_lengkap': 'Duplikat',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_envelope_error(response, 400)
        self.assertEqual(response.data['code'], 'VALIDATION_ERROR')
        self.assertIn('username', response.data['errors'])

    def test_register_password_too_short(self):
        response = self.client.post('/api/users/', {
            'username': 'pendek',
            'password': '12345',
            'nama_lengkap': 'Password Pendek',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_envelope_error(response, 400)
        self.assertIn('password', response.data['errors'])


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

    def test_me_patch_cannot_change_role(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        response = self.client.patch('/api/auth/me/', {
            'role': 'admin',
            'saldo': '999999.00',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'nasabah')
