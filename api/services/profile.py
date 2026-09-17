"""Helpers profil nasabah — kelengkapan alamat untuk gate transaksi (T2)."""

from __future__ import annotations

from rest_framework.exceptions import ValidationError

from api.models import User


def has_complete_address(user: User) -> bool:
    """Alamat teks wajib. Koordinat/wilayah opsional sampai Maps penuh."""
    return bool((user.alamat or '').strip())


def require_complete_address(user: User, action_label: str) -> None:
    """
    Blok transaksi jika alamat profil belum diisi.

    action_label contoh: 'mengajukan penjemputan', 'mengajukan penarikan',
    'menukar poin'.
    """
    if user.role != 'nasabah':
        return
    if has_complete_address(user):
        return
    raise ValidationError({
        'alamat': [
            f'Lengkapi alamat di profil sebelum {action_label}.',
        ],
    })
