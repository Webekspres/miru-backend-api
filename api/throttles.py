"""
Custom DRF throttle classes for MIRU Bank Sampah API.

Rate limits:
- Login endpoint: 10 requests/minute per anonymous IP
- Write endpoints: 100 requests/hour per authenticated user
"""

from rest_framework import permissions
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginAnonRateThrottle(AnonRateThrottle):
    """10 requests per minute untuk endpoint login (anonymous)."""

    scope = 'login'


class WriteUserRateThrottle(UserRateThrottle):
    """100 requests per hour untuk write operations per user.

    GET/HEAD/OPTIONS tidak di-throttle.
    """

    scope = 'write'

    def allow_request(self, request, view):
        # Safe methods (GET, HEAD, OPTIONS) — tidak di-throttle
        if request.method in permissions.SAFE_METHODS:
            return True
        return super().allow_request(request, view)
