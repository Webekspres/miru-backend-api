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
        self.assertIn('jam_buka', data)
        self.assertIn('jam_tutup', data)
        self.assertIn('pengumuman', data)
        self.assertIn('tentang', data)
        self.assertIn('kebijakan', data)
        self.assertIn('syarat_ketentuan', data)
        self.assertTrue(data['tentang'].strip())
        self.assertTrue(data['kebijakan'].strip())
        self.assertTrue(data['syarat_ketentuan'].strip())

    def test_terms_endpoint_public(self):
        response = self.client.get('/api/terms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response)
        data = response.data['data']
        self.assertEqual(data['versi'], '1.0')
        self.assertEqual(data['judul'], 'Syarat & Ketentuan MIRU Bank Sampah')
        self.assertIn('ringkasan', data)
        self.assertIn('konten', data)
        self.assertIn('#', data['konten'])
        self.assertIn('Penghapusan Akun', data['konten'])
        self.assertIn('/hapus-akun', data['konten'])

    def test_admin_can_patch_syarat_ketentuan(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            '/api/settings/',
            {'syarat_ketentuan': '# Syarat\n\nIsi syarat MIRU.'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('# Syarat', response.data['data']['syarat_ketentuan'])
        terms = self.client.get('/api/terms/')
        self.assertEqual(terms.status_code, status.HTTP_200_OK)
        self.assertIn('# Syarat', terms.data['data']['konten'])

    def test_admin_can_patch_jam_buka_tutup(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            '/api/settings/',
            {'jam_buka': '08:00:00', 'jam_tutup': '16:30:00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data['jam_buka'], '08:00:00')
        self.assertEqual(data['jam_tutup'], '16:30:00')
        self.assertIn('08.00', data['jam_operasional'])
        self.assertIn('16.30', data['jam_operasional'])

    def test_logo_url_ignored_on_patch(self):
        settings = PengaturanInstitusi.load()
        settings.logo_url = None
        settings.save()
        self.auth_as(self.admin)
        response = self.client.patch(
            '/api/settings/',
            {
                'nama_institusi': 'MIRU Logo Ignore',
                'logo_url': 'https://example.com/logo.png',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['nama_institusi'], 'MIRU Logo Ignore')
        self.assertIsNone(response.data['data']['logo_url'])
        settings.refresh_from_db()
        self.assertIsNone(settings.logo_url)

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

    def test_admin_can_patch_tentang_and_kebijakan(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            '/api/settings/',
            {
                'tentang': '# Tentang\n\nIsi tentang MIRU.',
                'kebijakan': '# Kebijakan\n\nIsi kebijakan.',
                'syarat_ketentuan': '# Syarat\n\nIsi syarat.',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('# Tentang', response.data['data']['tentang'])
        self.assertIn('# Kebijakan', response.data['data']['kebijakan'])
        self.assertIn('# Syarat', response.data['data']['syarat_ketentuan'])
        privacy = self.client.get('/api/privacy-policy/')
        self.assertEqual(privacy.status_code, status.HTTP_200_OK)
        self.assertIn('# Kebijakan', privacy.data['data']['konten'])
        terms = self.client.get('/api/terms/')
        self.assertEqual(terms.status_code, status.HTTP_200_OK)
        self.assertIn('# Syarat', terms.data['data']['konten'])

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
