from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class EnvelopeAPITestCase(APITestCase):
    """Base test case with envelope helpers and user factories."""

    def assert_envelope_success(self, response, status_code=200):
        self.assertTrue(response.data.get('success'), response.data)
        self.assertEqual(response.data.get('status_code'), status_code)
        self.assertIn('message', response.data)
        self.assertIn('meta', response.data)
        self.assertIn('timestamp', response.data['meta'])
        self.assertIn('request_id', response.data['meta'])

    def assert_envelope_error(self, response, status_code):
        self.assertFalse(response.data.get('success'), response.data)
        self.assertEqual(response.data.get('status_code'), status_code)
        self.assertIn('code', response.data)
        self.assertIsNone(response.data.get('data'))

    def create_nasabah(self, username='nasabah_test', password='secret12'):
        return User.objects.create_user(
            username=username,
            password=password,
            nama_lengkap='Nasabah Test',
            role='nasabah',
            no_hp='08123456789',
            alamat='Timika',
        )

    def create_admin(self, username='admin_test', password='secret12'):
        return User.objects.create_user(
            username=username,
            password=password,
            nama_lengkap='Admin Test',
            role='admin',
            no_hp='08123456780',
            alamat='Timika',
        )

    def create_koordinator(self, username='koordinator_test', password='secret12'):
        return User.objects.create_user(
            username=username,
            password=password,
            nama_lengkap='Koordinator Test',
            role='koordinator',
            no_hp='08123456781',
            alamat='Timika',
        )

    def create_petugas(self, username='petugas_test', password='secret12'):
        return User.objects.create_user(
            username=username,
            password=password,
            nama_lengkap='Petugas Test',
            role='petugas',
            no_hp='08123456782',
            alamat='Timika',
        )

    def auth_as(self, user, password='secret12'):
        login = self.client.post('/api/auth/login/', {
            'username': user.username,
            'password': password,
        }, format='json')
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login.data["data"]["access"]}'
        )
        return login.data['data']['access']
