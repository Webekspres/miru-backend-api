"""Konten edukasi — Markdown mentah (T8)."""

from rest_framework import status

from api.models import EDUKASI_MARKDOWN_SUBSET, KontenEdukasi

from .base import EnvelopeAPITestCase


class EdukasiMarkdownTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin(username='admin_edukasi')
        self.nasabah = self.create_nasabah(username='nasabah_edukasi')

    def test_admin_stores_raw_markdown(self):
        md = (
            '# Cara Pilah PET\n\n'
            'Gunakan **botol bersih**. Lihat [panduan](https://example.com).\n\n'
            '- Cuci\n- Keringkan\n\n'
            '`inline` dan:\n\n```\ncode block\n```\n'
        )
        self.auth_as(self.admin)
        response = self.client.post(
            '/api/edukasi/',
            {'judul': 'Pilah PET', 'isi': md, 'aktif': True, 'urutan': 1},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['isi'].rstrip('\n'), md.rstrip('\n'))
        obj = KontenEdukasi.objects.get(pk=response.data['data']['id'])
        self.assertEqual(obj.isi.rstrip('\n'), md.rstrip('\n'))
        self.assertIn('heading', EDUKASI_MARKDOWN_SUBSET)

    def test_public_list_returns_markdown_isi(self):
        KontenEdukasi.objects.create(
            judul='Tips',
            isi='## Tips\n\n*satu*',
            aktif=True,
            urutan=0,
        )
        self.auth_as(self.nasabah)
        response = self.client.get('/api/edukasi/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = response.data['data']
        self.assertTrue(any(i['isi'].startswith('## Tips') for i in items))
