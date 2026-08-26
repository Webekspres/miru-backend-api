"""Tests for in-app notification mark-as-read endpoints."""

from api.models import Notifikasi
from api.tests.base import EnvelopeAPITestCase


class NotificationMarkReadTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah()
        self.other = self.create_nasabah(username='other_nasabah')
        self.notif = Notifikasi.objects.create(
            user=self.nasabah,
            judul='Penjemputan Disetujui',
            deskripsi='Penjemputan sampah Anda telah disetujui.',
            kategori='penjemputan',
            is_read=False,
        )
        Notifikasi.objects.create(
            user=self.nasabah,
            judul='Setoran Selesai',
            deskripsi='Setoran Anda telah diproses.',
            kategori='setoran',
            is_read=False,
        )
        Notifikasi.objects.create(
            user=self.other,
            judul='Notif Lain',
            deskripsi='Milik user lain.',
            is_read=False,
        )

    def test_mark_one_as_read(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            f'/api/notifications/{self.notif.id}/read/',
            format='json',
        )
        self.assert_envelope_success(response, 200)
        self.notif.refresh_from_db()
        self.assertTrue(self.notif.is_read)
        self.assertTrue(response.data['data']['is_read'])

    def test_mark_all_as_read(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/notifications/mark-all-read/',
            {},
            format='json',
        )
        self.assert_envelope_success(response, 200)
        self.assertEqual(response.data['data']['updated_count'], 2)
        self.assertEqual(
            Notifikasi.objects.filter(user=self.nasabah, is_read=False).count(),
            0,
        )
        # Notifikasi user lain tidak ikut berubah
        self.assertEqual(
            Notifikasi.objects.filter(user=self.other, is_read=False).count(),
            1,
        )

    def test_cannot_mark_other_user_notification(self):
        other_notif = Notifikasi.objects.get(user=self.other)
        self.auth_as(self.nasabah)
        response = self.client.post(
            f'/api/notifications/{other_notif.id}/read/',
            format='json',
        )
        self.assertEqual(response.status_code, 404)
        other_notif.refresh_from_db()
        self.assertFalse(other_notif.is_read)

    def test_petugas_can_list_own_notifications(self):
        petugas = self.create_petugas()
        Notifikasi.objects.create(
            user=petugas,
            judul='Tugas Penjemputan Baru',
            deskripsi='Anda mendapat tugas menjemput sampah.',
            kategori='penjemputan',
        )
        Notifikasi.objects.create(
            user=self.nasabah,
            judul='Bukan milik petugas',
            deskripsi='Test',
        )
        self.auth_as(petugas)
        response = self.client.get('/api/notifications/')
        self.assert_envelope_success(response, 200)
        data = response.data['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['judul'], 'Tugas Penjemputan Baru')
