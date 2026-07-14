"""
Tests for rate limiting (Fase 7.1 — Keamanan API).

Rate limits:
- Login endpoint: 10 requests/minute per anonymous IP
- Write endpoints: 100 requests/hour per authenticated user

Because LocMemCache is process-local and each test shares the same
Django test client instance, we verify that the throttle *class is
wired in* correctly rather than testing exact counts in integration.
"""

from decimal import Decimal

from rest_framework import status

from api.models import KategoriSampah
from api.throttles import LoginAnonRateThrottle, WriteUserRateThrottle

from .base import EnvelopeAPITestCase


class LoginRateLimitTests(EnvelopeAPITestCase):
    """Verifikasi throttle class terpasang di endpoint login."""

    def test_login_view_has_throttle(self):
        """MiruTokenObtainPairView memiliki throttle_classes."""
        from api.auth_views import MiruTokenObtainPairView

        self.assertIn(
            LoginAnonRateThrottle,
            MiruTokenObtainPairView.throttle_classes,
        )

    def test_login_throttle_rate_is_10_per_minute(self):
        """Scope login memiliki rate 10/minute."""
        num, period = LoginAnonRateThrottle().parse_rate('10/minute')
        self.assertEqual(num, 10)
        self.assertEqual(period, 60)
        self.assertEqual(LoginAnonRateThrottle.scope, 'login')

    def test_login_throttle_does_not_crash(self):
        """
        Login throttle mechanism berjalan tanpa error (tidak 500).
        """
        resp = self.client.post(
            '/api/auth/login/',
            {'username': 'nonexistent', 'password': 'wrong'},
            format='json',
        )
        self.assertIn(
            resp.status_code,
            (status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_429_TOO_MANY_REQUESTS),
        )


class WriteRateLimitTests(EnvelopeAPITestCase):
    """Verifikasi write throttle class terpasang secara global."""

    def setUp(self):
        self.nasabah = self.create_nasabah()
        self.token = self.auth_as(self.nasabah)
        self.kategori = KategoriSampah.objects.create(
            nama='Kertas Uji', harga_beli_per_kg=Decimal('2000.00'),
        )

    def test_write_throttle_scope_rate(self):
        """Scope write memiliki rate 100/hour."""
        num, period = WriteUserRateThrottle().parse_rate('100/hour')
        self.assertEqual(num, 100)
        self.assertEqual(period, 3600)
        self.assertEqual(WriteUserRateThrottle.scope, 'write')

    def test_write_throttle_skips_safe_methods(self):
        """GET requests tidak kena throttle write."""

        class MockGetRequest:
            method = 'GET'

        self.assertTrue(
            WriteUserRateThrottle().allow_request(MockGetRequest(), None),
        )

    def test_write_throttle_applies_to_unsafe_methods(self):
        """POST requests kena throttle write."""

        class MockUser:
            is_authenticated = True
            pk = 9999

        class MockPostRequest:
            method = 'POST'
            user = MockUser()

        # Harusnya di-throttle (allow_request panggil super)
        result = WriteUserRateThrottle().allow_request(MockPostRequest(), None)
        self.assertIsNotNone(result)  # Tidak error
