from decimal import Decimal

from rest_framework import status

from api.models import PenukaranPoin, Reward

from .base import EnvelopeAPITestCase


class RedemptionCreateTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah(username='nasabah_rdm')
        self.nasabah.poin = 150
        self.nasabah.save()
        self.admin = self.create_admin(username='admin_rdm')
        self.koordinator = self.create_koordinator(username='koord_rdm')
        self.reward = Reward.objects.create(
            nama='Pulsa Rp10.000',
            poin_dibutuhkan=100,
            stok=5,
        )

    def test_nasabah_create_success(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/reward-redemptions/',
            {'reward': self.reward.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data['data']
        self.assertEqual(data['status'], 'menunggu')
        self.assertEqual(data['poin_dibutuhkan'], 100)
        self.assertEqual(data['reward_nama'], 'Pulsa Rp10.000')

    def test_reject_insufficient_poin(self):
        self.nasabah.poin = 50
        self.nasabah.save()
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/reward-redemptions/',
            {'reward': self.reward.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_empty_reward_stok(self):
        self.reward.stok = 0
        self.reward.save()
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/reward-redemptions/',
            {'reward': self.reward.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_cannot_create(self):
        self.auth_as(self.admin)
        response = self.client.post(
            '/api/reward-redemptions/',
            {'reward': self.reward.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RedemptionApproveTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah(username='nasabah_rdm2')
        self.nasabah.poin = 150
        self.nasabah.save()
        self.admin = self.create_admin(username='admin_rdm2')
        self.koordinator = self.create_koordinator(username='koord_rdm2')
        self.reward = Reward.objects.create(
            nama='Bibit',
            poin_dibutuhkan=50,
            stok=3,
        )
        self.redemption = PenukaranPoin.objects.create(
            nasabah=self.nasabah,
            reward=self.reward,
            status='menunggu',
        )

    def test_admin_approve_debits_poin_and_stok(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/reward-redemptions/{self.redemption.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'selesai')
        self.assertEqual(response.data['data']['poin_nasabah_baru'], 100)
        self.assertEqual(response.data['data']['stok_reward_baru'], 2)

        self.nasabah.refresh_from_db()
        self.reward.refresh_from_db()
        self.assertEqual(self.nasabah.poin, 100)
        self.assertEqual(self.reward.stok, 2)

    def test_koordinator_cannot_approve(self):
        self.auth_as(self.koordinator)
        response = self.client.patch(
            f'/api/reward-redemptions/{self.redemption.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nasabah_cannot_approve(self):
        self.auth_as(self.nasabah)
        response = self.client.patch(
            f'/api/reward-redemptions/{self.redemption.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_prevent_double_processing(self):
        self.redemption.status = 'selesai'
        self.redemption.save()
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/reward-redemptions/{self.redemption.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_approve_rejects_insufficient_poin(self):
        self.nasabah.poin = 10
        self.nasabah.save()
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/reward-redemptions/{self.redemption.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.nasabah.refresh_from_db()
        self.reward.refresh_from_db()
        self.assertEqual(self.nasabah.poin, 10)
        self.assertEqual(self.reward.stok, 3)

    def test_approve_rejects_empty_stok(self):
        self.reward.stok = 0
        self.reward.save()
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/reward-redemptions/{self.redemption.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.reward.refresh_from_db()
        self.assertEqual(self.reward.stok, 0)

    def test_nasabah_only_sees_own(self):
        other = self.create_nasabah(username='nasabah_other_rdm')
        PenukaranPoin.objects.create(
            nasabah=other,
            reward=self.reward,
            status='menunggu',
        )
        self.auth_as(self.nasabah)
        response = self.client.get('/api/reward-redemptions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['nasabah'], self.nasabah.id)
