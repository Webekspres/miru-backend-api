"""
Self-service hapus akun nasabah (kewajiban Play Store).

Akun TIDAK di-hard-delete karena catatan transaksi (setoran, penjemputan,
penarikan, penukaran poin, pengaduan) adalah catatan keuangan bank sampah
yang wajib dipertahankan (UU PDP Pasal 26 — kepentingan hukum/operasional).

Yang dilakukan:
- Data pribadi (PII) dihapus/dianonimkan: username, email, nama, no_hp,
  alamat, koordinat, patokan, avatar.
- Saldo & poin dinolkan, akun dinonaktifkan (is_active=False), password
  dibuat tidak terpakai sehingga tidak bisa login.
- Data sesi & notifikasi dihapus: OTP, token reset, device token FCM,
  notifikasi in-app.
"""

from __future__ import annotations

from django.db import transaction

from api.models import (
    AuditLog,
    DeviceToken,
    Notifikasi,
    PasswordResetToken,
    PhoneOTP,
)

ANONYMIZED_USERNAME_PREFIX = 'deleted_'
ANONYMIZED_DISPLAY_NAME = 'Akun Terhapus'


@transaction.atomic
def delete_nasabah_account(user) -> None:
    """Anonimkan & nonaktifkan akun nasabah (soft delete)."""
    original_username = user.username

    # Bersihkan data sesi & notifikasi milik user
    Notifikasi.objects.filter(user=user).delete()
    DeviceToken.objects.filter(user=user).delete()
    PhoneOTP.objects.filter(user=user).delete()
    PasswordResetToken.objects.filter(user=user).delete()

    # Anonimkan seluruh PII
    user.username = f'{ANONYMIZED_USERNAME_PREFIX}{user.pk}'
    user.email = ''
    user.first_name = ''
    user.last_name = ''
    user.nama_lengkap = ANONYMIZED_DISPLAY_NAME
    user.no_hp = ''
    user.phone_verified = False
    user.alamat = ''
    user.patokan = ''
    user.avatar_url = ''
    user.latitude = None
    user.longitude = None
    user.kelurahan = None
    user.rt = ''
    user.rw = ''
    user.saldo = 0
    user.poin = 0
    user.setuju_kebijakan_data = False
    user.tanggal_persetujuan_kebijakan = None
    user.is_active = False
    user.is_staff = False
    user.set_unusable_password()
    user.save()

    # Tandai di audit log bahwa ini penghapusan mandiri (bukan dari admin)
    AuditLog.objects.create(
        user=None,
        action='delete',
        model_name='User',
        object_id=str(user.pk),
        changes={
            'metode': 'self_service_deletion',
            'username_asli': original_username,
        },
    )
