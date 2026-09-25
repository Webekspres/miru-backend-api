from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from api.models import PoinTransaksi

from .base import EnvelopeAPITestCase


class PoinInfoTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah(username='poin_user')
        self.auth_as(self.nasabah)

    def _batch(self, sisa, days, expired=False):
        return PoinTransaksi.objects.create(
            user=self.nasabah, jumlah=sisa, sisa=sisa,
            tanggal_kedaluwarsa=timezone.now() + timedelta(days=days),
            is_expired=expired,
        )

    def test_empty(self):
        response = self.client.get('/api/auth/poin-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data['total_akan_hangus'], 0)
        self.assertEqual(data['poin_hangus_terdekat'], 0)
        self.assertIsNone(data['tanggal_kedaluwarsa_terdekat'])

    def test_nearest_expiry_only_counts_nearest_date(self):
        self._batch(10, days=30)
        self._batch(5, days=30)
        self._batch(40, days=200)
        self._batch(99, days=-1, expired=True)
        self._batch(0, days=10)

        data = self.client.get('/api/auth/poin-info/').data['data']
        self.assertEqual(data['total_akan_hangus'], 55)
        self.assertEqual(data['poin_hangus_terdekat'], 15)
        self.assertIsNotNone(data['tanggal_kedaluwarsa_terdekat'])

    def test_requires_auth(self):
        self.client.credentials()
        response = self.client.get('/api/auth/poin-info/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
