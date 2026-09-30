from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APIClient

from api.models import Pengumuman

from .base import EnvelopeAPITestCase


class PengumumanKelolaTests(EnvelopeAPITestCase):
    """Admin/koordinator menerbitkan pengumuman yang tampil di beranda aplikasi."""

    def setUp(self):
        self.admin = self.create_admin(username='admin_umum')
        self.koordinator = self.create_koordinator(username='koord_umum')
        self.nasabah = self.create_nasabah(username='nasabah_umum')

    @patch('api.services.fcm.send_to_user_ids')
    def test_admin_publishes_announcement_visible_publicly_and_pushed(self, mock_push):
        self.auth_as(self.admin)
        response = self.client.post(
            '/api/pengumuman/kelola/',
            {'judul': 'Bank sampah libur 17 Agustus', 'isi': 'Penjemputan diliburkan.'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(mock_push.called)

        public = APIClient().get('/api/pengumuman/')
        self.assertIn('Bank sampah libur 17 Agustus', [p['judul'] for p in public.data['data']])

    def test_deactivate_hides_from_app_and_delete_removes(self):
        item = Pengumuman.objects.create(judul='Lama', isi='x', aktif=True)
        self.auth_as(self.koordinator)
        off = self.client.patch(f'/api/pengumuman/kelola/{item.id}/', {'aktif': False}, format='json')
        self.assertEqual(off.status_code, status.HTTP_200_OK)
        self.assertEqual(APIClient().get('/api/pengumuman/').data['data'], [])

        self.assertEqual(self.client.delete(f'/api/pengumuman/kelola/{item.id}/').status_code, 200)
        self.assertFalse(Pengumuman.objects.filter(pk=item.id).exists())

    def test_nasabah_cannot_manage(self):
        self.auth_as(self.nasabah)
        response = self.client.post('/api/pengumuman/kelola/', {'judul': 'x', 'isi': 'y'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
