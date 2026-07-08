from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import TokenError

from .response import error_envelope


def _flatten_errors(detail, prefix=''):
    if isinstance(detail, list):
        return {prefix: detail} if prefix else {'non_field_errors': detail}
    if isinstance(detail, dict):
        errors = {}
        for key, value in detail.items():
            field = f'{prefix}.{key}' if prefix else key
            if isinstance(value, (list, dict)):
                errors.update(_flatten_errors(value, field))
            else:
                errors[field] = [str(value)]
        return errors
    return {prefix or 'non_field_errors': [str(detail)]}


def _get_error_code(exc, status_code: int) -> str:
    if status_code == 400:
        return 'VALIDATION_ERROR'
    if isinstance(exc, ValidationError):
        code = getattr(exc, 'default_code', None)
        if code and str(code).upper() not in ('INVALID',):
            return str(code).upper()
        return 'VALIDATION_ERROR'
    if isinstance(exc, APIException):
        code = getattr(exc, 'default_code', None)
        if code and str(code).lower() not in ('error', 'invalid'):
            return str(code).upper()
    mapping = {
        400: 'VALIDATION_ERROR',
        401: 'AUTHENTICATION_FAILED',
        403: 'PERMISSION_DENIED',
        404: 'NOT_FOUND',
        405: 'METHOD_NOT_ALLOWED',
        409: 'CONFLICT',
        429: 'RATE_LIMIT_EXCEEDED',
        500: 'INTERNAL_ERROR',
    }
    return mapping.get(status_code, 'ERROR')


def _get_error_message(exc, status_code: int) -> str:
    if isinstance(exc, ValidationError):
        return 'Satu atau lebih field tidak valid.'
    if status_code == 401:
        return 'Autentikasi gagal. Silakan login kembali.'
    if status_code == 403:
        return 'Anda tidak memiliki izin untuk melakukan aksi ini.'
    if status_code == 404:
        return 'Data tidak ditemukan.'
    if status_code == 405:
        return 'Metode HTTP tidak diizinkan.'
    if status_code >= 500:
        return 'Terjadi kesalahan pada server.'
    detail = getattr(exc, 'detail', str(exc))
    if isinstance(detail, str):
        return detail
    return 'Permintaan tidak dapat diproses.'


def miru_exception_handler(exc, context):
    if isinstance(exc, TokenError):
        request = context.get('request')
        envelope = error_envelope(
            message='Token tidak valid atau sudah kedaluwarsa.',
            status_code=status.HTTP_401_UNAUTHORIZED,
            code='AUTHENTICATION_FAILED',
            errors={'detail': [str(exc)]},
            request=request,
        )
        from rest_framework.response import Response
        return Response(envelope, status=status.HTTP_401_UNAUTHORIZED)

    response = exception_handler(exc, context)
    request = context.get('request')

    if response is not None:
        status_code = response.status_code
        errors = None
        if isinstance(exc, ValidationError):
            errors = _flatten_errors(exc.detail)
        elif isinstance(response.data, dict):
            errors = _flatten_errors(response.data)
        elif isinstance(response.data, list):
            errors = {'non_field_errors': response.data}

        envelope = error_envelope(
            message=_get_error_message(exc, status_code),
            status_code=status_code,
            code=_get_error_code(exc, status_code),
            errors=errors,
            request=request,
        )
        response.data = envelope
        return response

    if isinstance(exc, APIException):
        status_code = exc.status_code
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    envelope = error_envelope(
        message=_get_error_message(exc, status_code),
        status_code=status_code,
        code=_get_error_code(exc, status_code),
        errors=None,
        request=request,
    )
    from rest_framework.response import Response

    return Response(envelope, status=status_code)
