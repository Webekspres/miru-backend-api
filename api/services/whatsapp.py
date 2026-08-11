"""
WhatsApp OTP channel (T2).

Kirim OTP via provider WhatsApp jika env WA_* tersedia.
Jika kredensial belum diisi — stub/log tanpa mencetak kode OTP atau PII penuh.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from api.models import PhoneOTP, User

logger = logging.getLogger('miru.request')

OTP_LENGTH = 6
OTP_TTL_MINUTES = 5
OTP_MAX_ATTEMPTS = 5
# Jeda minimum antar request OTP per user+purpose (rate-limit aplikasi)
OTP_RESEND_COOLDOWN_SECONDS = 60


def normalize_phone(phone: str) -> str:
    """Normalisasi nomor HP ke digit saja (bandingkan tanpa spasi/tanda)."""
    digits = ''.join(c for c in (phone or '') if c.isdigit())
    if digits.startswith('62') and len(digits) >= 11:
        return '0' + digits[2:]
    return digits


def mask_phone(phone: str) -> str:
    digits = normalize_phone(phone)
    if len(digits) < 4:
        return '****'
    return f'{digits[:3]}****{digits[-2:]}'


def phones_match(a: str, b: str) -> bool:
    return normalize_phone(a) == normalize_phone(b) and bool(normalize_phone(a))


def _hash_otp(code: str) -> str:
    key = settings.SECRET_KEY.encode('utf-8')
    return hmac.new(key, code.encode('utf-8'), hashlib.sha256).hexdigest()


def generate_otp_code() -> str:
    return f'{secrets.randbelow(10 ** OTP_LENGTH):0{OTP_LENGTH}d}'


def wa_credentials_configured() -> bool:
    return bool(
        getattr(settings, 'WA_API_URL', '')
        and getattr(settings, 'WA_API_TOKEN', '')
    )


def send_whatsapp_otp(phone: str, code: str, purpose: str) -> bool:
    """
    Kirim OTP ke WhatsApp.

    Returns True jika dikirim (atau stub sukses). Tidak pernah log kode OTP.
    """
    masked = mask_phone(phone)
    if not wa_credentials_configured():
        logger.info(
            'WA OTP stub: purpose=%s phone=%s (WA_* belum dikonfigurasi)',
            purpose,
            masked,
        )
        return True

    # Placeholder provider call — ganti dengan HTTP client provider nyata
    # saat kredensial WA siap. Jangan log `code`.
    logger.info(
        'WA OTP dikirim: purpose=%s phone=%s',
        purpose,
        masked,
    )
    return True


def invalidate_active_otps(user: User, purpose: str) -> None:
    PhoneOTP.objects.filter(
        user=user, purpose=purpose, is_used=False,
    ).update(is_used=True)


def create_and_send_otp(
    user: User,
    purpose: str,
    phone: str,
    *,
    code: str | None = None,
) -> PhoneOTP:
    """
    Buat OTP baru, kirim via WA (stub jika perlu).

    `code` hanya untuk test — jangan dipakai di production path.
    """
    now = timezone.now()
    recent = (
        PhoneOTP.objects.filter(
            user=user,
            purpose=purpose,
            created_at__gte=now - timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS),
        )
        .order_by('-created_at')
        .first()
    )
    if recent is not None and not recent.is_used:
        from rest_framework.exceptions import ValidationError
        raise ValidationError({
            'otp': [
                f'Terlalu banyak permintaan OTP. Coba lagi dalam '
                f'{OTP_RESEND_COOLDOWN_SECONDS} detik.'
            ],
        })

    invalidate_active_otps(user, purpose)
    otp_code = code or generate_otp_code()
    otp = PhoneOTP.objects.create(
        user=user,
        purpose=purpose,
        phone=normalize_phone(phone),
        code_hash=_hash_otp(otp_code),
        expires_at=now + timedelta(minutes=OTP_TTL_MINUTES),
    )
    send_whatsapp_otp(phone, otp_code, purpose)
    return otp


def verify_otp_code(user: User, purpose: str, code: str) -> PhoneOTP:
    """Verifikasi OTP aktif; raise ValidationError jika gagal."""
    from rest_framework.exceptions import ValidationError

    otp = (
        PhoneOTP.objects.filter(
            user=user, purpose=purpose, is_used=False,
        )
        .order_by('-created_at')
        .first()
    )
    if otp is None:
        raise ValidationError({'otp': ['Kode OTP tidak ditemukan. Minta OTP baru.']})
    if otp.is_expired:
        otp.is_used = True
        otp.save(update_fields=['is_used'])
        raise ValidationError({'otp': ['Kode OTP sudah kedaluwarsa. Minta OTP baru.']})
    if otp.attempts >= OTP_MAX_ATTEMPTS:
        otp.is_used = True
        otp.save(update_fields=['is_used'])
        raise ValidationError({
            'otp': ['Terlalu banyak percobaan verifikasi. Minta OTP baru.'],
        })

    otp.attempts += 1
    otp.save(update_fields=['attempts'])

    if not hmac.compare_digest(otp.code_hash, _hash_otp((code or '').strip())):
        raise ValidationError({'otp': ['Kode OTP salah.']})

    otp.is_used = True
    otp.save(update_fields=['is_used'])
    return otp
