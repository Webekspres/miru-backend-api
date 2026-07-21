"""
Firebase Cloud Messaging (FCM) — Fase 8.6.

Kirim push notification ke device token milik user.
Payload TIDAK boleh berisi NIK, KTP, JWT, atau secret (Security §11).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from django.conf import settings

logger = logging.getLogger('miru.request')

# Hanya kunci data yang diizinkan di FCM data payload.
ALLOWED_DATA_KEYS = frozenset({
    'kategori',
    'notification_id',
    'pengumuman_id',
    'event',
})

_FORBIDDEN_KEY_RE = re.compile(
    r'(nik|ktp|password|passwd|secret|authorization|jwt|bearer|access_token|refresh_token)',
    re.IGNORECASE,
)

_firebase_app = None
_init_attempted = False


def _credentials_ready() -> bool:
    return bool(
        getattr(settings, 'FCM_ENABLED', False)
        and (
            getattr(settings, 'FIREBASE_CREDENTIALS_FILE', '')
            or getattr(settings, 'FIREBASE_CREDENTIALS_JSON', '')
        )
    )


def _get_firebase_app():
    """Lazy-init firebase_admin app. Returns None jika FCM off / gagal."""
    global _firebase_app, _init_attempted

    if _firebase_app is not None:
        return _firebase_app
    if _init_attempted:
        return None
    _init_attempted = True

    if not _credentials_ready():
        logger.info('FCM nonaktif atau kredensial belum dikonfigurasi.')
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials

        if firebase_admin._apps:
            _firebase_app = firebase_admin.get_app()
            return _firebase_app

        file_path = getattr(settings, 'FIREBASE_CREDENTIALS_FILE', '')
        raw_json = getattr(settings, 'FIREBASE_CREDENTIALS_JSON', '')

        if file_path:
            cred = credentials.Certificate(file_path)
        else:
            cred = credentials.Certificate(json.loads(raw_json))

        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info('Firebase Admin diinisialisasi untuk FCM.')
        return _firebase_app
    except Exception as exc:
        logger.error('Gagal init Firebase Admin: %s', exc)
        return None


def sanitize_fcm_data(data: dict[str, Any] | None) -> dict[str, str]:
    """
    Bangun data payload aman: allowlist key + tolak key/value sensitif.
    Semua value dikonversi ke string (syarat FCM data messages).
    """
    if not data:
        return {}

    safe: dict[str, str] = {}
    for key, value in data.items():
        if key not in ALLOWED_DATA_KEYS:
            logger.warning('FCM: key data ditolak (bukan allowlist): %s', key)
            continue
        if _FORBIDDEN_KEY_RE.search(key):
            logger.warning('FCM: key data ditolak (sensitif): %s', key)
            continue
        str_val = '' if value is None else str(value)
        if _FORBIDDEN_KEY_RE.search(str_val):
            logger.warning('FCM: value data ditolak (sensitif) untuk key=%s', key)
            continue
        safe[key] = str_val
    return safe


def build_notification_payload(
    *,
    kategori: str,
    notification_id: int | None = None,
    pengumuman_id: int | None = None,
    event: str | None = None,
) -> dict[str, str]:
    """Payload data standar untuk event notifikasi MIRU."""
    raw: dict[str, Any] = {'kategori': kategori}
    if notification_id is not None:
        raw['notification_id'] = notification_id
    if pengumuman_id is not None:
        raw['pengumuman_id'] = pengumuman_id
    if event is not None:
        raw['event'] = event
    return sanitize_fcm_data(raw)


def send_to_tokens(
    tokens: list[str],
    *,
    title: str,
    body: str,
    data: dict[str, Any] | None = None,
) -> int:
    """
    Kirim FCM ke daftar token. Hapus token invalid (UNREGISTERED).

    Returns:
        Jumlah sukses dikirim.
    """
    if not tokens:
        return 0

    app = _get_firebase_app()
    if app is None:
        return 0

    safe_data = sanitize_fcm_data(data)
    # Jangan kirim device/auth token di payload — sudah di-sanitize via allowlist.

    try:
        from firebase_admin import messaging

        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data=safe_data,
            tokens=tokens,
        )
        response = messaging.send_each_for_multicast(message)

        # Bersihkan token yang sudah tidak valid
        invalid: list[str] = []
        for idx, send_response in enumerate(response.responses):
            if send_response.success:
                continue
            exc = send_response.exception
            code = getattr(exc, 'code', '') or ''
            if 'UNREGISTERED' in str(exc) or 'registration-token-not-registered' in str(exc).lower() or code == 'NOT_FOUND':
                invalid.append(tokens[idx])

        if invalid:
            from api.models import DeviceToken
            deleted, _ = DeviceToken.objects.filter(token__in=invalid).delete()
            logger.info('FCM: %s device token invalid dihapus.', deleted)

        success = response.success_count
        if response.failure_count:
            logger.warning(
                'FCM partial fail: success=%s failure=%s',
                success,
                response.failure_count,
            )
        return success
    except Exception as exc:
        logger.error('Gagal kirim FCM: %s', exc)
        return 0


def send_to_user(
    user_id: int,
    *,
    title: str,
    body: str,
    data: dict[str, Any] | None = None,
) -> int:
    """Kirim FCM ke semua device token milik user."""
    from api.models import DeviceToken

    tokens = list(
        DeviceToken.objects.filter(user_id=user_id).values_list('token', flat=True)
    )
    return send_to_tokens(tokens, title=title, body=body, data=data)


def send_to_user_ids(
    user_ids: list[int],
    *,
    title: str,
    body: str,
    data: dict[str, Any] | None = None,
) -> int:
    """Kirim FCM ke semua device token milik daftar user."""
    if not user_ids:
        return 0
    from api.models import DeviceToken

    tokens = list(
        DeviceToken.objects.filter(user_id__in=user_ids)
        .values_list('token', flat=True)
        .distinct()
    )
    return send_to_tokens(tokens, title=title, body=body, data=data)


def trigger_fcm_for_notification(notification) -> None:
    """Hook setelah Notifikasi in-app dibuat — failsafe."""
    try:
        send_to_user(
            notification.user_id,
            title=notification.judul,
            body=notification.deskripsi,
            data=build_notification_payload(
                kategori=notification.kategori,
                notification_id=notification.id,
                event=notification.kategori,
            ),
        )
    except Exception as exc:
        logger.error('Gagal trigger FCM notifikasi#%s: %s', notification.id, exc)
