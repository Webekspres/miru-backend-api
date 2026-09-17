import secrets

from django.test import override_settings
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.authentication import ACCESS_COOKIE_NAME, CSRF_COOKIE_NAME, REFRESH_COOKIE_NAME

from .base import EnvelopeAPITestCase


class CookieAuthTestCase(EnvelopeAPITestCase):
    """Base cookie-auth test.

    Sebagian besar pengujian memakai cookie yang di-seed langsung di test
    client (bukan lewat endpoint login) supaya total login per run tidak
    melampaui throttle anon 10/menit/ip. Hanya pengujian yang spesifik
    mengecek perilaku endpoint login yang memakai login sungguhan.
    """

    def seed_cookie_session(self, username='cookie_seed', password='secret12'):
        """Buat user + pasang cookie access/refresh/csrf seolah-olah baru login."""
        user = self.create_nasabah(username=username, password=password)
        refresh = RefreshToken.for_user(user)
        self.csrf_token = secrets.token_urlsafe(32)
        self.client.cookies[ACCESS_COOKIE_NAME] = str(refresh.access_token)
        self.client.cookies[REFRESH_COOKIE_NAME] = str(refresh)
        self.client.cookies[CSRF_COOKIE_NAME] = self.csrf_token
        return user, str(refresh)


class CookieAuthLoginTests(CookieAuthTestCase):
    """Login harus mengembalikan token di body (kompatibilitas mobile) DAN
    men-set cookie HttpOnly (web admin)."""

    def setUp(self):
        self.user = self.create_nasabah(username='cookie_user', password='secret12')

    def test_login_sets_httponly_cookies_and_csrf_cookie(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'cookie_user',
            'password': 'secret12',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Body tetap ada (mobile masih baca access/refresh dari JSON)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])

        cookies = response.cookies
        self.assertIn(ACCESS_COOKIE_NAME, cookies)
        self.assertIn(REFRESH_COOKIE_NAME, cookies)
        self.assertIn(CSRF_COOKIE_NAME, cookies)

        self.assertEqual(cookies[ACCESS_COOKIE_NAME]['httponly'], True)
        self.assertEqual(cookies[REFRESH_COOKIE_NAME]['httponly'], True)
        # CSRF cookie sengaja BUKAN httponly — harus bisa dibaca JS
        self.assertEqual(cookies[CSRF_COOKIE_NAME]['httponly'], '')
        self.assertEqual(cookies[ACCESS_COOKIE_NAME]['samesite'], 'Lax')

    @override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver'])
    def test_cookies_are_secure_when_debug_false(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'cookie_user',
            'password': 'secret12',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies[ACCESS_COOKIE_NAME]['secure'], True)

    def test_login_ignores_bogus_access_cookie_from_previous_session(self):
        """Cookie access_token basi/tidak valid yang masih nempel di browser
        tidak boleh membuat endpoint AllowAny (login) gagal."""
        self.client.cookies[ACCESS_COOKIE_NAME] = 'not-a-real-jwt'
        response = self.client.post('/api/auth/login/', {
            'username': 'cookie_user',
            'password': 'secret12',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CookieAuthRequestTests(CookieAuthTestCase):
    """Setelah login (cookie tersimpan otomatis di test client), request
    berikutnya harus terautentikasi lewat cookie tanpa header Authorization."""

    def setUp(self):
        self.user, _ = self.seed_cookie_session(username='cookie_user2')

    def test_get_authenticates_via_cookie_only(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['username'], 'cookie_user2')

    def test_unsafe_method_without_csrf_header_is_rejected(self):
        response = self.client.patch('/api/auth/me/', {
            'username': 'cookie_user2_renamed',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'cookie_user2')

    def test_unsafe_method_with_wrong_csrf_header_is_rejected(self):
        response = self.client.patch(
            '/api/auth/me/',
            {'username': 'cookie_user2_renamed'},
            format='json',
            HTTP_X_CSRFTOKEN='wrong-token-value',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unsafe_method_with_correct_csrf_header_succeeds(self):
        response = self.client.patch(
            '/api/auth/me/',
            {'username': 'cookie_user2_renamed'},
            format='json',
            HTTP_X_CSRFTOKEN=self.csrf_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'cookie_user2_renamed')


class CookieAuthMobileHeaderUnaffectedTests(CookieAuthTestCase):
    """Klien mobile (header Authorization, tanpa cookie sama sekali) tidak
    boleh terkena pengecekan CSRF sama sekali."""

    def setUp(self):
        self.user = self.create_nasabah(username='mobile_user', password='secret12')

    def test_unsafe_method_via_header_needs_no_csrf(self):
        self.auth_as(self.user)
        response = self.client.patch('/api/auth/me/', {
            'username': 'mobile_user_renamed',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CookieAuthRefreshTests(CookieAuthTestCase):
    def setUp(self):
        self.user, _ = self.seed_cookie_session(username='cookie_refresh_user')

    def test_refresh_uses_cookie_when_body_empty(self):
        old_access_cookie = self.client.cookies[ACCESS_COOKIE_NAME].value
        response = self.client.post('/api/auth/refresh/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
        # Cookie access_token baru ikut di-set ulang oleh response refresh.
        self.assertIn(ACCESS_COOKIE_NAME, response.cookies)
        self.assertNotEqual(response.cookies[ACCESS_COOKIE_NAME].value, old_access_cookie)


class CookieAuthLogoutTests(CookieAuthTestCase):
    def setUp(self):
        self.user, self.refresh_token = self.seed_cookie_session(username='cookie_logout_user')

    def test_logout_clears_cookies_and_blacklists_refresh_token(self):
        response = self.client.post(
            '/api/auth/logout/', {}, format='json',
            HTTP_X_CSRFTOKEN=self.csrf_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for name in (ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME, CSRF_COOKIE_NAME):
            self.assertIn(name, response.cookies)
            self.assertEqual(response.cookies[name].value, '')

        # Refresh token yang sudah di-logout tidak boleh bisa dipakai lagi.
        refresh_attempt = self.client.post('/api/auth/refresh/', {
            'refresh': self.refresh_token,
        }, format='json')
        self.assertEqual(refresh_attempt.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_csrf_is_rejected(self):
        self.client.cookies.clear()
        response = self.client.post('/api/auth/logout/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_clears_cookies_when_access_token_expired(self):
        """Access token sudah basi, tapi csrf cookie masih ada → logout tetap
        berhasil dan cookie HttpOnly ikut dihapus (mencegah redirect loop
        di proxy edge guard karena cookie basi tidak bisa dihapus lewat JS)."""
        self.client.cookies[ACCESS_COOKIE_NAME] = 'expired-or-invalid-jwt'
        response = self.client.post(
            '/api/auth/logout/', {}, format='json',
            HTTP_X_CSRFTOKEN=self.csrf_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for name in (ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME, CSRF_COOKIE_NAME):
            self.assertIn(name, response.cookies)
            self.assertEqual(response.cookies[name].value, '')


class CookieAuthMobileLogoutTests(CookieAuthTestCase):
    """Klien mobile logout via Bearer header (access valid) + refresh di body —
    tanpa cookie, tanpa CSRF, dan tanpa jalur hapus-cookie."""

    def setUp(self):
        self.user, self.refresh_token = self.seed_cookie_session(username='cookie_mobile_logout')
        self.auth_as(self.user)

    def test_mobile_logout_blacklists_refresh_without_cookie(self):
        self.client.cookies.clear()
        response = self.client.post('/api/auth/logout/', {
            'refresh': self.refresh_token,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_attempt = self.client.post('/api/auth/refresh/', {
            'refresh': self.refresh_token,
        }, format='json')
        self.assertEqual(refresh_attempt.status_code, status.HTTP_401_UNAUTHORIZED)