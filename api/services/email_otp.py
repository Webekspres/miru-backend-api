"""OTP lewat email (pengganti WhatsApp selama biaya WA belum memungkinkan).

Hash, masa berlaku, batas percobaan dan verifikasi memakai helper yang sama
dengan OTP WhatsApp (`verify_otp_code`). Tambahan anti-spam per alamat email.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from api.models import PhoneOTP, User
from api.services.whatsapp import (
    OTP_RESEND_COOLDOWN_SECONDS,
    OTP_TTL_MINUTES,
    _hash_otp,
    generate_otp_code,
    get_dev_fixed_otp,
    invalidate_active_otps,
)

logger = logging.getLogger('miru.request')

# Batas kirim OTP ke satu alamat email (semua akun & tujuan digabung).
OTP_EMAIL_MAX_PER_HOUR = 3
OTP_EMAIL_MAX_PER_DAY = 6

# Domain email sekali pakai yang umum dipakai bot.
DISPOSABLE_DOMAINS = frozenset({
    'mailinator.com', 'guerrillamail.com', 'guerrillamail.net', 'sharklasers.com',
    '10minutemail.com', 'temp-mail.org', 'tempmail.com', 'tempmail.net',
    'yopmail.com', 'trashmail.com', 'getnada.com', 'dispostable.com',
    'maildrop.cc', 'throwawaymail.com', 'fakeinbox.com', 'emailondeck.com',
    'mintemail.com', 'mohmal.com', 'tempail.com', 'moakt.com',
})

_PURPOSE_SUBJECT = {
    PhoneOTP.PURPOSE_REGISTRATION: 'Kode verifikasi pendaftaran MIRU',
    PhoneOTP.PURPOSE_EMAIL_VERIFY: 'Kode verifikasi email MIRU',
    PhoneOTP.PURPOSE_PASSWORD_RESET: 'Kode reset kata sandi MIRU',
    PhoneOTP.PURPOSE_ACCOUNT_DELETION: 'Kode konfirmasi hapus akun MIRU',
}


def normalize_email(email: str) -> str:
    return (email or '').strip().lower()


def mask_email(email: str) -> str:
    """'budi.santoso@gmail.com' → 'bu***@gmail.com'."""
    local, _, domain = normalize_email(email).partition('@')
    if not domain:
        return '***'
    return f'{local[:2]}***@{domain}'


def emails_match(a: str, b: str) -> bool:
    return bool(normalize_email(a)) and normalize_email(a) == normalize_email(b)


def skip_otp_enabled() -> bool:
    return bool(getattr(settings, 'SKIP_OTP_VERIFICATION', False))


def validate_email_target(email: str, user: User) -> str:
    """Validasi format, domain sekali pakai, dan email belum dipakai akun lain."""
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError as DjangoValidationError

    email = normalize_email(email)
    if not email:
        raise ValidationError({'email': ['Email wajib diisi.']})
    try:
        validate_email(email)
    except DjangoValidationError:
        raise ValidationError({'email': ['Format email tidak valid.']})
    if email.rsplit('@', 1)[1] in DISPOSABLE_DOMAINS:
        raise ValidationError({
            'email': ['Email sementara tidak diizinkan. Gunakan email pribadi Anda.'],
        })
    if (
        User.objects.filter(email__iexact=email, email_verified=True)
        .exclude(pk=user.pk).exists()
    ):
        raise ValidationError({'email': ['Email sudah dipakai akun lain.']})
    return email


def _check_limits(user: User, purpose: str, email: str) -> None:
    now = timezone.now()
    if PhoneOTP.objects.filter(
        user=user, purpose=purpose, is_used=False,
        created_at__gte=now - timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS),
    ).exists():
        raise ValidationError({
            'otp': [
                f'Terlalu banyak permintaan OTP. Coba lagi dalam '
                f'{OTP_RESEND_COOLDOWN_SECONDS} detik.'
            ],
        })
    sent = PhoneOTP.objects.filter(email__iexact=email)
    if sent.filter(created_at__gte=now - timedelta(hours=1)).count() >= OTP_EMAIL_MAX_PER_HOUR:
        raise ValidationError({
            'email': ['Terlalu banyak kode dikirim ke email ini. Coba lagi dalam 1 jam.'],
        })
    if sent.filter(created_at__gte=now - timedelta(days=1)).count() >= OTP_EMAIL_MAX_PER_DAY:
        raise ValidationError({
            'email': ['Batas pengiriman kode ke email ini hari ini sudah tercapai.'],
        })


def send_email_otp(email: str, code: str, purpose: str) -> bool:
    subject = _PURPOSE_SUBJECT.get(purpose, 'Kode OTP MIRU')
    body = (
        f'Kode OTP Anda: {code}\n\n'
        f'Kode berlaku {OTP_TTL_MINUTES} menit. Jangan berikan kode ini kepada '
        f'siapa pun, termasuk petugas MIRU.\n\n'
        f'Jika Anda tidak meminta kode ini, abaikan email ini.\n\n'
        f'— MIRU Bank Sampah, Distrik Mimika Baru'
    )
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        return True
    except Exception as exc:  # jangan log kode OTP / alamat lengkap
        logger.error('Gagal kirim OTP email ke %s (%s): %s', mask_email(email), purpose, exc)
        return False


def create_and_send_email_otp(user: User, purpose: str, email: str) -> PhoneOTP:
    email = normalize_email(email)
    _check_limits(user, purpose, email)
    invalidate_active_otps(user, purpose)
    code = get_dev_fixed_otp() or generate_otp_code()
    otp = PhoneOTP.objects.create(
        user=user,
        purpose=purpose,
        email=email,
        code_hash=_hash_otp(code),
        expires_at=timezone.now() + timedelta(minutes=OTP_TTL_MINUTES),
    )
    if not send_email_otp(email, code, purpose):
        otp.is_used = True
        otp.save(update_fields=['is_used'])
        raise ValidationError({
            'email': ['Email gagal dikirim. Periksa alamat email atau coba lagi nanti.'],
        })
    return otp


def is_pending_registration(user: User) -> bool:
    """Nasabah yang baru mendaftar dan belum pernah aktif.

    Beda dengan akun yang sengaja dinonaktifkan admin (pernah login) — akun
    itu tidak boleh aktif lagi hanya karena memverifikasi email.
    """
    return (
        user.role == 'nasabah'
        and not user.is_active
        and user.last_login is None
        and not user.email_verified
    )


def mark_email_verified(user: User, email: str, *, activate: bool) -> None:
    """Simpan email terverifikasi; `activate` hanya untuk pendaftaran baru."""
    user.email = normalize_email(email)
    user.email_verified = True
    fields = ['email', 'email_verified']
    if activate and not user.is_active:
        user.is_active = True
        fields.append('is_active')
    user.save(update_fields=fields)
