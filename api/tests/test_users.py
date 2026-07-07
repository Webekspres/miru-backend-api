from django.contrib.auth import get_user_model
from rest_framework import status

from .base import EnvelopeAPITestCase

User = get_user_model()


class UserListFilterTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin()
        self.create_nasabah(username='budi_nasabah')
        self.create_nasabah(username='ani_nasabah')
        User.objects.create_user(
            username='petugas1',
            password='secret12',
            nama_lengkap='Petugas Satu',
            role='petugas',
        )
        self.auth_as(self.admin)

    def test_list_users_as_admin(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        self.assertIn('pagination', response.data['meta'])
        self.assertGreaterEqual(len(response.data['data']), 3)

    def test_list_users_forbidden_for_nasabah(self):
        nasabah = self.create_nasabah(username='list_denied')
        self.auth_as(nasabah)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_envelope_error(response, 403)

    def test_filter_by_role(self):
        response = self.client.get('/api/users/?role=nasabah')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        roles = {u['role'] for u in response.data['data']}
        self.assertEqual(roles, {'nasabah'})

    def test_filter_by_is_active(self):
        inactive = self.create_nasabah(username='inactive_user')
        inactive.is_active = False
        inactive.save()

        response = self.client.get('/api/users/?is_active=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {u['username'] for u in response.data['data']}
        self.assertIn('inactive_user', usernames)

    def test_search_users(self):
        response = self.client.get('/api/users/?search=budi')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {u['username'] for u in response.data['data']}
        self.assertIn('budi_nasabah', usernames)


class UserPatchPermissionTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah(username='patch_me', password='secret12')
        self.other = self.create_nasabah(username='other_user', password='secret12')
        self.admin = self.create_admin()
        self.auth_as(self.nasabah, password='secret12')

    def test_nasabah_patch_own_profile(self):
        response = self.client.patch(
            f'/api/users/{self.nasabah.id}/',
            {'nama_lengkap': 'Nama Baru', 'no_hp': '08111111111'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        self.assertEqual(response.data['data']['nama_lengkap'], 'Nama Baru')

    def test_nasabah_cannot_patch_other_user(self):
        response = self.client.patch(
            f'/api/users/{self.other.id}/',
            {'nama_lengkap': 'Hack'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_envelope_error(response, 403)

    def test_nasabah_cannot_change_role_saldo_poin(self):
        self.nasabah.saldo = 5000
        self.nasabah.poin = 10
        self.nasabah.save()

        response = self.client.patch(
            f'/api/users/{self.nasabah.id}/',
            {'role': 'admin', 'saldo': '99999.00', 'poin': 999},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.nasabah.refresh_from_db()
        self.assertEqual(self.nasabah.role, 'nasabah')
        self.assertEqual(self.nasabah.saldo, 5000)
        self.assertEqual(self.nasabah.poin, 10)

    def test_admin_can_patch_other_user(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/users/{self.nasabah.id}/',
            {'nama_lengkap': 'Diubah Admin', 'role': 'nasabah'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['nama_lengkap'], 'Diubah Admin')


class AdminCreateStaffTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin()
        self.auth_as(self.admin)

    def test_admin_create_petugas(self):
        response = self.client.post('/api/users/', {
            'username': 'petugas_baru',
            'password': 'secret12',
            'role': 'petugas',
            'nama_lengkap': 'Petugas Baru',
            'no_hp': '08122222222',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assert_envelope_success(response, 201)
        data = response.data['data']
        self.assertEqual(data['role'], 'petugas')
        self.assertNotIn('password', data)

        user = User.objects.get(username='petugas_baru')
        self.assertEqual(user.role, 'petugas')
        self.assertTrue(user.check_password('secret12'))

    def test_admin_create_koordinator(self):
        response = self.client.post('/api/users/', {
            'username': 'koordinator_baru',
            'password': 'secret12',
            'role': 'koordinator',
            'nama_lengkap': 'Koordinator Baru',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['role'], 'koordinator')

    def test_admin_cannot_create_nasabah_via_staff_endpoint(self):
        response = self.client.post('/api/users/', {
            'username': 'nasabah_admin',
            'password': 'secret12',
            'role': 'nasabah',
            'nama_lengkap': 'Nasabah Admin',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_envelope_error(response, 400)
        self.assertIn('role', response.data['errors'])

    def test_public_registration_still_nasabah_only(self):
        self.client.credentials()
        response = self.client.post('/api/users/', {
            'username': 'nasabah_publik',
            'password': 'secret12',
            'nama_lengkap': 'Nasabah Publik',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['role'], 'nasabah')


class UserResponseSecurityTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin()
        self.nasabah = self.create_nasabah(username='secure_user', password='secret12')
        self.auth_as(self.admin)

    def test_password_not_in_list_response(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user in response.data['data']:
            self.assertNotIn('password', user)

    def test_password_not_in_detail_response(self):
        response = self.client.get(f'/api/users/{self.nasabah.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('password', response.data['data'])
