from rest_framework import status

from api.models import PengaturanInstitusi, Pengumuman

from .base import EnvelopeAPITestCase


class InstitutionSettingsTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin(username='admin_settings')
        self.nasabah = self.create_nasabah(username='nasabah_settings')
        PengaturanInstitusi.load()
        Pengumuman.objects.create(
            judul='Pengumuman Aktif',
            isi='Isi pengumuman aktif.',
            aktif=True,
        )
        Pengumuman.objects.create(
            judul='Pengumuman Nonaktif',
            isi='Tidak ditampilkan.',
            aktif=False,
        )

    def test_get_settings_public_no_auth(self):
        response = self.client.get('/api/settings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response)
        data = response.data['data']
        self.assertIn('nama_institusi', data)
        self.assertIn('alamat', data)
        self.assertIn('kontak', data)
        self.assertIn('email', data)
        self.assertIn('jam_operasional', data)
        self.assertIn('pengumuman', data)

    def test_admin_can_patch_settings(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            '/api/settings/',
            {
                'nama_institusi': 'MIRU Bank Sampah Updated',
                'kontak': '08111111111',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['data']['nama_institusi'],
            'MIRU Bank Sampah Updated',
        )

        settings = PengaturanInstitusi.load()
        self.assertEqual(settings.nama_institusi, 'MIRU Bank Sampah Updated')
        self.assertEqual(settings.kontak, '08111111111')

    def test_nasabah_cannot_patch_settings(self):
        self.auth_as(self.nasabah)
        response = self.client.patch(
            '/api/settings/',
            {'nama_institusi': 'Hack'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_pengumuman_public_lists_active_only(self):
        response = self.client.get('/api/pengumuman/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['judul'], 'Pengumuman Aktif')
        self.assertTrue(response.data['data'][0]['aktif'])

    def test_singleton_settings_always_pk_one(self):
        settings = PengaturanInstitusi.load()
        settings.nama_institusi = 'Test Singleton'
        settings.save()
        reloaded = PengaturanInstitusi.load()
        self.assertEqual(reloaded.pk, 1)
        self.assertEqual(reloaded.nama_institusi, 'Test Singleton')
        self.assertEqual(PengaturanInstitusi.objects.count(), 1)
