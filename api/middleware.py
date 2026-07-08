import uuid
import threading

_thread_locals = threading.local()


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
