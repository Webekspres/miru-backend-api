from rest_framework import status

from api.models import Pengaduan

from .base import EnvelopeAPITestCase


class ComplaintCreateTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah(username='nasabah_cmp')
        self.admin = self.create_admin(username='admin_cmp')

    def _payload(self, **overrides):
        payload = {
            'jenis_pengaduan': 'saldo_belum_masuk',
            'keluhan': 'Setoran kemarin belum masuk ke saldo.',
        }
        payload.update(overrides)
        return payload

    def test_nasabah_create_success(self):
        self.auth_as(self.nasabah)
        response = self.client.post('/api/complaints/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data['data']
        self.assertEqual(data['status'], 'terbuka')
        self.assertEqual(data['jenis_pengaduan'], 'saldo_belum_masuk')
        self.assertEqual(data['tindak_lanjut'], '')

    def test_reject_invalid_jenis(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/complaints/',
            self._payload(jenis_pengaduan='invalid'),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_jenis_lainnya(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/complaints/',
            self._payload(jenis_pengaduan='lainnya', keluhan='Lain-lain.'),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['jenis_pengaduan'], 'lainnya')

    def test_create_notifies_admin(self):
        from api.models import Notifikasi
        self.auth_as(self.nasabah)
        response = self.client.post('/api/complaints/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        admin_notif = Notifikasi.objects.filter(
            user=self.admin, kategori='pengaduan', judul='Pengaduan Baru',
        )
        self.assertTrue(admin_notif.exists())
        nasabah_notif = Notifikasi.objects.filter(
            user=self.nasabah, kategori='pengaduan', judul='Pengaduan Diterima',
        )
        self.assertTrue(nasabah_notif.exists())

    def test_admin_cannot_create(self):
        self.auth_as(self.admin)
        response = self.client.post('/api/complaints/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ComplaintManageTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah(username='nasabah_cmp2')
        self.admin = self.create_admin(username='admin_cmp2')
        self.koordinator = self.create_koordinator(username='koord_cmp2')
        self.complaint = Pengaduan.objects.create(
            nasabah=self.nasabah,
            jenis_pengaduan='penjemputan_terlambat',
            keluhan='Petugas terlambat datang.',
            status='terbuka',
        )

    def test_admin_close_with_tindak_lanjut(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/complaints/{self.complaint.id}/',
            {
                'tindak_lanjut': 'Sudah dikonfirmasi ke nasabah via WA.',
                'status': 'ditutup',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'ditutup')

    def test_close_requires_tindak_lanjut(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/complaints/{self.complaint.id}/',
            {'status': 'ditutup'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tindak_lanjut', str(response.data))

    def test_close_rejects_blank_tindak_lanjut(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/complaints/{self.complaint.id}/',
            {'status': 'ditutup', 'tindak_lanjut': '   '},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('tindak_lanjut', response.data.get('errors', {}))

    def test_koordinator_cannot_update(self):
        self.auth_as(self.koordinator)
        response = self.client.patch(
            f'/api/complaints/{self.complaint.id}/',
            {'status': 'ditutup', 'tindak_lanjut': 'Test'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nasabah_cannot_update(self):
        self.auth_as(self.nasabah)
        response = self.client.patch(
            f'/api/complaints/{self.complaint.id}/',
            {'status': 'ditutup'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nasabah_only_sees_own(self):
        other = self.create_nasabah(username='nasabah_other_cmp')
        Pengaduan.objects.create(
            nasabah=other,
            jenis_pengaduan='kesalahan_data',
            keluhan='Data salah.',
            status='terbuka',
        )
        self.auth_as(self.nasabah)
        response = self.client.get('/api/complaints/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_filter_by_status_and_jenis(self):
        Pengaduan.objects.create(
            nasabah=self.nasabah,
            jenis_pengaduan='harga_tidak_sesuai',
            keluhan='Harga tidak sesuai.',
            status='ditutup',
            tindak_lanjut='Sudah dijelaskan.',
        )
        self.auth_as(self.admin)
        response = self.client.get(
            '/api/complaints/?status=ditutup&jenis_pengaduan=harga_tidak_sesuai',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
