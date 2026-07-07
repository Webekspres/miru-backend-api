from decimal import Decimal

from rest_framework import status

from api.models import KategoriSampah

from .base import EnvelopeAPITestCase


class WasteCategoryPublicReadTests(EnvelopeAPITestCase):
    def setUp(self):
        self.category = KategoriSampah.objects.create(
            nama='PET',
            harga_beli_per_kg=Decimal('3000.00'),
            stok_terkini_kg=Decimal('150.50'),
        )

    def test_list_public_without_auth(self):
        response = self.client.get('/api/waste-categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        self.assertIn('pagination', response.data['meta'])
        self.assertGreaterEqual(len(response.data['data']), 1)
        item = next(c for c in response.data['data'] if c['id'] == self.category.id)
        self.assertEqual(item['nama'], 'PET')
        self.assertEqual(item['harga_beli_per_kg'], '3000.00')
        self.assertEqual(item['stok_terkini_kg'], '150.50')

    def test_retrieve_public_without_auth(self):
        response = self.client.get(f'/api/waste-categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        data = response.data['data']
        self.assertEqual(data['nama'], 'PET')
        self.assertIn('stok_terkini_kg', data)
        self.assertEqual(data['stok_terkini_kg'], '150.50')


class WasteCategoryAdminCrudTests(EnvelopeAPITestCase):
    def setUp(self):
        self.admin = self.create_admin()
        self.koordinator = self.create_koordinator()
        self.nasabah = self.create_nasabah(username='nasabah_kat')
        self.category = KategoriSampah.objects.create(
            nama='Kardus',
            harga_beli_per_kg=Decimal('1500.00'),
            stok_terkini_kg=Decimal('75.00'),
        )

    def test_create_as_admin(self):
        self.auth_as(self.admin)
        response = self.client.post('/api/waste-categories/', {
            'nama': 'Kertas',
            'harga_beli_per_kg': '2000.00',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assert_envelope_success(response, 201)
        data = response.data['data']
        self.assertEqual(data['nama'], 'Kertas')
        self.assertEqual(data['harga_beli_per_kg'], '2000.00')
        self.assertEqual(data['stok_terkini_kg'], '0.00')

    def test_create_as_koordinator(self):
        self.auth_as(self.koordinator)
        response = self.client.post('/api/waste-categories/', {
            'nama': 'Aluminium',
            'harga_beli_per_kg': '10000.00',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assert_envelope_success(response, 201)

    def test_create_forbidden_for_nasabah(self):
        self.auth_as(self.nasabah)
        response = self.client.post('/api/waste-categories/', {
            'nama': 'Besi',
            'harga_beli_per_kg': '3000.00',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_envelope_error(response, 403)

    def test_patch_as_admin(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/waste-categories/{self.category.id}/',
            {'harga_beli_per_kg': '1800.00'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        self.assertEqual(response.data['data']['harga_beli_per_kg'], '1800.00')
        self.assertEqual(response.data['data']['stok_terkini_kg'], '75.00')

    def test_cannot_set_stok_via_create_or_patch(self):
        self.auth_as(self.admin)
        create = self.client.post('/api/waste-categories/', {
            'nama': 'Kaca',
            'harga_beli_per_kg': '500.00',
            'stok_terkini_kg': '999.00',
        }, format='json')
        self.assertEqual(create.data['data']['stok_terkini_kg'], '0.00')

        patch = self.client.patch(
            f'/api/waste-categories/{self.category.id}/',
            {'stok_terkini_kg': '999.00'},
            format='json',
        )
        self.assertEqual(patch.data['data']['stok_terkini_kg'], '75.00')

    def test_delete_as_admin(self):
        self.auth_as(self.admin)
        response = self.client.delete(f'/api/waste-categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(KategoriSampah.objects.filter(id=self.category.id).exists())

    def test_delete_forbidden_for_koordinator(self):
        self.auth_as(self.koordinator)
        response = self.client.delete(f'/api/waste-categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_envelope_error(response, 403)

    def test_duplicate_nama_rejected(self):
        self.auth_as(self.admin)
        response = self.client.post('/api/waste-categories/', {
            'nama': 'Kardus',
            'harga_beli_per_kg': '2000.00',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_envelope_error(response, 400)
        self.assertIn('nama', response.data['errors'])
