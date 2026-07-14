import logging
import time
import uuid
import threading

_thread_locals = threading.local()
logger = logging.getLogger('miru.request')


def get_current_request():
    """Access the current request from thread-local storage (for signals etc.)."""
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    """Get the current user from thread-local storage."""
    request = get_current_request()
    if request and hasattr(request, 'user'):
        return request.user
    return None


def get_client_ip(request) -> str | None:
    """Extract client IP from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = request.headers.get(
            'X-Request-ID',
            f'req_{uuid.uuid4().hex[:12]}',
        )
        response = self.get_response(request)
        response['X-Request-ID'] = request.request_id
        return response


class CurrentRequestMiddleware:
    """Store the current request in thread-local storage."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        try:
            response = self.get_response(request)
        finally:
            _thread_locals.request = None
        return response


class RequestLoggingMiddleware:
    """
    Middleware untuk mencatat setiap request dalam format JSON.

    - Mencatat method, path, status_code, duration, user, IP, request_id
    - Mencatat status code spike (4xx/5xx) dengan level WARNING/ERROR
    - Log dihasilkan dalam format JSON (terintegrasi dengan JSONFormatter)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time
        status_code = response.status_code
        method = request.method
        path = request.path
        request_id = getattr(request, 'request_id', '-')
        ip = get_client_ip(request) or '-'

        user_id = '-'
        user_role = '-'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = request.user.pk
            user_role = request.user.role

        log_data = {
            'method': method,
            'path': path,
            'status': status_code,
            'duration_ms': round(duration * 1000, 2),
            'user_id': user_id,
            'user_role': user_role,
            'ip': ip,
            'request_id': request_id,
        }

        # Pilih level log berdasarkan status code
        if status_code >= 500:
            logger.error(f'Request {method} {path} -> {status_code}', extra={'extra_fields': log_data})
        elif status_code >= 400:
            logger.warning(f'Request {method} {path} -> {status_code}', extra={'extra_fields': log_data})
        else:
            logger.info(f'Request {method} {path} -> {status_code}', extra={'extra_fields': log_data})

        return response
