import uuid

from django.utils import timezone
from rest_framework.response import Response


def get_request_id(request) -> str:
    if request is None:
        return f'req_{uuid.uuid4().hex[:12]}'
    return getattr(request, 'request_id', f'req_{uuid.uuid4().hex[:12]}')


def build_meta(request=None, extra: dict | None = None) -> dict:
    meta = {
        'timestamp': timezone.localtime(timezone.now()).isoformat(),
        'request_id': get_request_id(request),
    }
    if extra:
        meta.update(extra)
    return meta


def success_envelope(
    data,
    message: str = 'Permintaan berhasil.',
    status_code: int = 200,
    request=None,
    meta: dict | None = None,
) -> dict:
    envelope_meta = build_meta(request)
    if meta:
        envelope_meta.update(meta)
    return {
        'success': True,
        'status_code': status_code,
        'message': message,
        'data': data,
        'meta': envelope_meta,
    }


def error_envelope(
    message: str,
    status_code: int = 400,
    code: str = 'ERROR',
    errors=None,
    request=None,
    meta: dict | None = None,
) -> dict:
    envelope_meta = build_meta(request)
    if meta:
        envelope_meta.update(meta)
    return {
        'success': False,
        'status_code': status_code,
        'message': message,
        'code': code,
        'data': None,
        'errors': errors,
        'meta': envelope_meta,
    }


def success_response(
    data=None,
    message: str = 'Permintaan berhasil.',
    status_code: int = 200,
    request=None,
    meta: dict | None = None,
) -> Response:
    return Response(
        success_envelope(data, message, status_code, request, meta),
        status=status_code,
    )


def error_response(
    message: str,
    status_code: int = 400,
    code: str = 'ERROR',
    errors=None,
    request=None,
    meta: dict | None = None,
) -> Response:
    return Response(
        error_envelope(message, status_code, code, errors, request, meta),
        status=status_code,
    )


def get_action_message(action: str | None, method: str, status_code: int) -> str:
    messages = {
        'list': 'Daftar data berhasil diambil.',
        'retrieve': 'Data berhasil diambil.',
        'create': 'Data berhasil dibuat.',
        'update': 'Data berhasil diperbarui.',
        'partial_update': 'Data berhasil diperbarui.',
        'destroy': 'Data berhasil dihapus.',
    }
    if action and action in messages:
        return messages[action]
    if status_code == 201:
        return 'Data berhasil dibuat.'
    if status_code == 204:
        return 'Data berhasil dihapus.'
    if method == 'GET':
        return 'Data berhasil diambil.'
    if method in ('POST', 'PUT', 'PATCH'):
        return 'Permintaan berhasil.'
    return 'Permintaan berhasil.'
