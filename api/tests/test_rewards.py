from rest_framework import status

from api.models import Reward

from .base import EnvelopeAPITestCase


class RewardPublicListTests(EnvelopeAPITestCase):
    def setUp(self):
        self.reward = Reward.objects.create(
            nama='Pulsa Rp10.000',
            poin_dibutuhkan=100,
            stok=50,
        )

    def test_list_public_without_auth(self):
        response = self.client.get('/api/rewards/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        self.assertIn('pagination', response.data['meta'])
        item = next(r for r in response.data['data'] if r['id'] == self.reward.id)
        self.assertEqual(item['nama'], 'Pulsa Rp10.000')
        self.assertEqual(item['poin_dibutuhkan'], 100)
        self.assertEqual(item['stok'], 50)

    def test_retrieve_public_without_auth(self):
        response = self.client.get(f'/api/rewards/{self.reward.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        data = response.data['data']
        self.assertEqual(data['poin_dibutuhkan'], 100)
        self.assertEqual(data['stok'], 50)


class RewardAdminCrudTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin()
        self.koordinator = self.create_koordinator()
        self.nasabah = self.create_nasabah(username='nasabah_rwd')
        self.reward = Reward.objects.create(
            nama='Bibit Tanaman',
            poin_dibutuhkan=50,
            stok=30,
        )

    def test_create_as_admin(self):
        self.auth_as(self.admin)
        response = self.client.post('/api/rewards/', {
            'nama': 'Sembako',
            'poin_dibutuhkan': 200,
            'stok': 10,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assert_envelope_success(response, 201)
        data = response.data['data']
        self.assertEqual(data['nama'], 'Sembako')
        self.assertEqual(data['poin_dibutuhkan'], 200)
        self.assertEqual(data['stok'], 10)

    def test_koordinator_cannot_create(self):
        self.auth_as(self.koordinator)
        response = self.client.post('/api/rewards/', {
            'nama': 'Blocked',
            'poin_dibutuhkan': 50,
            'stok': 5,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nasabah_cannot_create(self):
        self.auth_as(self.nasabah)
        response = self.client.post('/api/rewards/', {
            'nama': 'Blocked',
            'poin_dibutuhkan': 50,
            'stok': 5,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_as_admin(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/rewards/{self.reward.id}/',
            {'stok': 25, 'poin_dibutuhkan': 60},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['stok'], 25)
        self.assertEqual(response.data['data']['poin_dibutuhkan'], 60)

    def test_reject_invalid_poin(self):
        self.auth_as(self.admin)
        response = self.client.post('/api/rewards/', {
            'nama': 'Invalid',
            'poin_dibutuhkan': 0,
            'stok': 5,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_as_admin(self):
        self.auth_as(self.admin)
        response = self.client.delete(f'/api/rewards/{self.reward.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Reward.objects.filter(id=self.reward.id).exists())
