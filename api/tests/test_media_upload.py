"""Unggah gambar edukasi + sajian /objects/ (filesystem fallback)."""

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from api.models import KontenEdukasi

from .base import EnvelopeAPITestCase

# PNG 1x1 transparan
TINY_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
    b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
    b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
    b'\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
)


class MediaUploadTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin(username='admin_media')
        self.nasabah = self.create_nasabah(username='nasabah_media')

    def _png(self, name='cover.png'):
        return SimpleUploadedFile(name, TINY_PNG, content_type='image/png')

    def test_admin_upload_returns_key_and_url(self):
        self.auth_as(self.admin)
        response = self.client.post(
            '/api/media/uploads/',
            {'file': self._png(), 'purpose': 'edukasi'},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data['data']
        self.assertTrue(data['key'].startswith('edukasi/'))
        self.assertTrue(data['key'].endswith('.webp'))
        self.assertEqual(data['content_type'], 'image/webp')
        self.assertIn('/objects/', data['url'])
        self.assertIn(data['key'], data['url'])

    def test_nasabah_cannot_upload_edukasi(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/media/uploads/',
            {'file': self._png(), 'purpose': 'edukasi'},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_upload_konten(self):
        self.auth_as(self.admin)
        response = self.client.post(
            '/api/media/uploads/',
            {'file': self._png(), 'purpose': 'konten'},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['data']['key'].startswith('konten/'))
        self.assertTrue(response.data['data']['key'].endswith('.webp'))

    def test_nasabah_can_upload_avatar(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/media/uploads/',
            {'file': self._png(), 'purpose': 'avatar'},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data['data']
        self.assertTrue(data['key'].startswith('avatar/'))
        self.assertTrue(data['key'].endswith('.webp'))

    def test_rejects_non_image(self):
        self.auth_as(self.admin)
        fake = SimpleUploadedFile('note.txt', b'hello world', content_type='text/plain')
        response = self.client.post(
            '/api/media/uploads/',
            {'file': fake, 'purpose': 'edukasi'},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_public_object_is_readable_without_auth(self):
        self.auth_as(self.admin)
        uploaded = self.client.post(
            '/api/media/uploads/',
            {'file': self._png(), 'purpose': 'edukasi'},
            format='multipart',
        )
        key = uploaded.data['data']['key']
        self.client.credentials()
        response = self.client.get(f'/objects/{key}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'image/webp')
        body = b''.join(response.streaming_content)
        self.assertTrue(body.startswith(b'RIFF'))
        self.assertIn(b'WEBP', body[:16])

    def test_rejects_path_traversal(self):
        response = self.client.get('/objects/edukasi/../ktp/secret.jpg')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class EdukasiGambarUrlTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin(username='admin_gambar')
        self.nasabah = self.create_nasabah(username='nasabah_gambar')

    def test_admin_stores_object_key_from_absolute_url(self):
        self.auth_as(self.admin)
        response = self.client.post(
            '/api/edukasi/',
            {
                'judul': 'Pilah botol',
                'isi': 'Cuci dulu.',
                'gambar_url': 'http://localhost:8000/objects/edukasi/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.png',
                'aktif': True,
                'urutan': 1,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = KontenEdukasi.objects.get(pk=response.data['data']['id'])
        self.assertEqual(
            obj.gambar_url,
            'edukasi/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.png',
        )
        self.assertIn('/objects/edukasi/', response.data['data']['gambar_url'])

    def test_featured_image_alias_writes_gambar_url(self):
        self.auth_as(self.admin)
        response = self.client.post(
            '/api/edukasi/',
            {
                'judul': 'Alias',
                'isi': 'Isi',
                'featured_image': 'https://cdn.example.com/banner.jpg',
                'aktif': True,
                'urutan': 0,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = KontenEdukasi.objects.get(pk=response.data['data']['id'])
        self.assertEqual(obj.gambar_url, 'https://cdn.example.com/banner.jpg')
        self.assertEqual(
            response.data['data']['featured_image'],
            'https://cdn.example.com/banner.jpg',
        )

    def test_public_list_includes_gambar_url(self):
        KontenEdukasi.objects.create(
            judul='Tips',
            isi='## Tips',
            gambar_url='https://cdn.example.com/tips.jpg',
            aktif=True,
        )
        self.auth_as(self.nasabah)
        response = self.client.get('/api/edukasi/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        match = next(i for i in response.data['data'] if i['judul'] == 'Tips')
        self.assertEqual(match['gambar_url'], 'https://cdn.example.com/tips.jpg')


class AvatarUrlTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah(username='nasabah_avatar')

    def test_patch_me_stores_avatar_key(self):
        self.auth_as(self.nasabah)
        uploaded = self.client.post(
            '/api/media/uploads/',
            {
                'file': SimpleUploadedFile('face.png', TINY_PNG, content_type='image/png'),
                'purpose': 'avatar',
            },
            format='multipart',
        )
        url = uploaded.data['data']['url']
        response = self.client.patch(
            '/api/auth/me/',
            {'avatar_url': url},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.nasabah.refresh_from_db()
        self.assertTrue(self.nasabah.avatar_url.startswith('avatar/'))
        self.assertTrue(self.nasabah.avatar_url.endswith('.webp'))
        self.assertIn('/objects/avatar/', response.data['data']['avatar_url'])
