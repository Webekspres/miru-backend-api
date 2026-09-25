from rest_framework import status

from api.models import WilayahLayanan
from api.services.wilayah import KELURAHAN_MIMIKA_BARU

from .base import EnvelopeAPITestCase


class CakupanWilayahTests(EnvelopeAPITestCase):
    def test_public_cascade_locked_to_mimika_baru(self):
        WilayahLayanan.objects.create(kelurahan='Kuala Kencana', aktif=False)

        response = self.client.get('/api/wilayah/cakupan/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data['provinsi']['nama'], 'Papua Tengah')
        self.assertEqual(data['kabupaten']['kode'], '94.04')
        self.assertEqual(data['distrik']['nama'], 'Mimika Baru')
        names = [k['nama'] for k in data['kelurahan']]
        self.assertEqual(len(names), len(KELURAHAN_MIMIKA_BARU))
        self.assertNotIn('Kuala Kencana', names)
        self.assertIn('Distrik Mimika Baru', data['pesan'])
        nayaro = next(k for k in data['kelurahan'] if k['nama'] == 'Nayaro')
        self.assertEqual((nayaro['kode'], nayaro['jenis']), ('94.04.01.2004', 'kampung'))


class KelurahanValidationTests(EnvelopeAPITestCase):
    def setUp(self):
        self.resmi = WilayahLayanan.objects.get(kode='94.04.01.1002')  # Kwamki
        self.luar = WilayahLayanan.objects.create(kelurahan='Kuala Kencana', aktif=False)

    def test_nasabah_cannot_pick_inactive_kelurahan(self):
        nasabah = self.create_nasabah()
        self.auth_as(nasabah)

        response = self.client.patch('/api/auth/me/', {'kelurahan': self.luar.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('kelurahan', response.data['errors'])

        response = self.client.patch('/api/auth/me/', {'kelurahan': self.resmi.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        nasabah.refresh_from_db()
        self.assertEqual(nasabah.kelurahan_id, self.resmi.id)

    def test_admin_cannot_assign_inactive_kelurahan(self):
        self.auth_as(self.create_admin())
        response = self.client.post('/api/users/', {
            'username': 'warga_luar', 'password': 'secret12', 'role': 'nasabah',
            'nama_lengkap': 'Warga Luar', 'setuju_kebijakan_data': True,
            'kelurahan': self.luar.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('kelurahan', response.data['errors'])
