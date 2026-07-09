from rest_framework import status

from .base import EnvelopeAPITestCase


class HealthCheckTests(EnvelopeAPITestCase):
    def test_health_returns_ok(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_envelope_success(response, 200)
        data = response.data['data']
        self.assertEqual(data['status'], 'ok')
        self.assertIn('database', data)

    def test_health_is_public_no_auth(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health_has_correct_envelope(self):
        response = self.client.get('/health/')
        body = response.data
        self.assertTrue(body['success'])
        self.assertEqual(body['status_code'], 200)
        self.assertEqual(body['message'], 'Server berjalan normal.')
        self.assertIn('meta', body)
        self.assertIn('request_id', body['meta'])
        self.assertIn('timestamp', body['meta'])

    def test_health_response_structure(self):
        response = self.client.get('/health/')
        data = response.data['data']
        self.assertIn('status', data)
        self.assertIn('database', data)
        self.assertIsInstance(data['status'], str)
        self.assertIsInstance(data['database'], str)
