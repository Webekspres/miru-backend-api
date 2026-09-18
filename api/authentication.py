"""Autentikasi JWT ganda: header `Authorization: Bearer …` (mobile, tidak
berubah) dan cookie HttpOnly (web admin). Jalur cookie memakai proteksi CSRF
double-submit karena browser mengirim cookie secara ambien pada setiap
request ke domain ini — berbeda dari header Authorization yang harus
di-attach eksplisit oleh kode JS/app dan karenanya kebal CSRF.
"""
import hmac
import secrets

from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

ACCESS_COOKIE_NAME = 'access_token'
REFRESH_COOKIE_NAME = 'refresh_token'
CSRF_COOKIE_NAME = 'csrf_token'
CSRF_HEADER_NAME = 'X-CSRFToken'

_SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


class CookieOrHeaderJWTAuthentication(JWTAuthentication):
    """Header hadir → perilaku identik dengan `JWTAuthentication` bawaan
    (dipakai mobile). Header tidak ada → coba cookie `access_token` (web);
    cookie yang tidak ada/tidak valid dianggap anonim (bukan error keras)
    supaya endpoint `AllowAny` seperti login/refresh tetap bisa diakses saat
    cookie kosong atau kedaluwarsa.
    """

    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        raw_token = request.COOKIES.get(ACCESS_COOKIE_NAME)
        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except exceptions.AuthenticationFailed:
            return None

        user = self.get_user(validated_token)

        if request.method not in _SAFE_METHODS:
            self._enforce_csrf(request)

        return user, validated_token

    def _enforce_csrf(self, request) -> None:
        csrf_cookie = request.COOKIES.get(CSRF_COOKIE_NAME, '')
        csrf_header = request.headers.get(CSRF_HEADER_NAME, '')
        if not csrf_cookie or not csrf_header or not hmac.compare_digest(csrf_cookie, csrf_header):
            raise exceptions.PermissionDenied(
                'CSRF token tidak valid atau tidak ditemukan.'
            )
