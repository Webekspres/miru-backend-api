"""Pickup request validation and status state machine."""

from datetime import timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from api.exceptions import InvalidStatusTransitionError
from api.models import Penjemputan, User

MIN_ESTIMASI_BERAT_KG = Decimal('5')
WIT = ZoneInfo('Asia/Jayapura')

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    'menunggu': {'disetujui', 'ditolak'},
    'disetujui': {'dijadwalkan'},
    'dijadwalkan': {'dalam_perjalanan'},
    'dalam_perjalanan': {'dijemput'},
    'dijemput': {'selesai'},
    'selesai': set(),
    'ditolak': set(),
}

ADMIN_TRANSITIONS = {
    ('menunggu', 'disetujui'),
    ('menunggu', 'ditolak'),
    ('disetujui', 'dijadwalkan'),
}

PETUGAS_TRANSITIONS = {
    ('dijadwalkan', 'dalam_perjalanan'),
    ('dalam_perjalanan', 'dijemput'),
    ('dijemput', 'selesai'),
}


def validate_estimasi_berat(berat: Decimal) -> Decimal:
    if berat < MIN_ESTIMASI_BERAT_KG:
        raise ValidationError('Minimal estimasi berat penjemputan 5 kg.')
    return berat


def validate_jadwal_h_plus_one(jadwal) -> None:
    now_wit = timezone.now().astimezone(WIT)
    min_date = now_wit.date() + timedelta(days=1)

    if timezone.is_naive(jadwal):
        jadwal_date = jadwal.date()
    else:
        jadwal_date = jadwal.astimezone(WIT).date()

    if jadwal_date < min_date:
        raise ValidationError(
            'Jadwal penjemputan minimal H+1 (besok atau setelahnya).'
        )


def validate_nasabah_owner(user: User, nasabah: User | None = None) -> User:
    if user.role != 'nasabah':
        raise PermissionDenied('Hanya nasabah yang dapat mengajukan penjemputan.')
    if nasabah is not None and nasabah.pk != user.pk:
        raise ValidationError('Nasabah hanya dapat mengajukan penjemputan untuk diri sendiri.')
    return user


def validate_petugas_user(petugas: User) -> User:
    if petugas.role != 'petugas':
        raise ValidationError('Petugas yang ditugaskan harus berperan petugas.')
    if not petugas.is_active:
        raise ValidationError('Petugas tidak aktif.')
    return petugas


def validate_status_transition(
    instance: Penjemputan,
    new_status: str,
    user: User,
    petugas: User | None = None,
) -> None:
    current_status = instance.status

    if new_status == current_status:
        return

    allowed = ALLOWED_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise InvalidStatusTransitionError(
            f"Tidak dapat mengubah status dari '{current_status}' ke '{new_status}'."
        )

    transition = (current_status, new_status)

    if transition in ADMIN_TRANSITIONS:
        if user.role != 'admin':
            raise PermissionDenied('Hanya admin yang dapat menyetujui, menolak, atau menjadwalkan penjemputan.')
        if new_status == 'dijadwalkan':
            assigned = petugas if petugas is not None else instance.petugas
            if assigned is None:
                raise ValidationError({'petugas': ['Petugas wajib ditugaskan saat menjadwalkan.']})
            validate_petugas_user(assigned)
        return

    if transition in PETUGAS_TRANSITIONS:
        if user.role == 'admin':
            return
        if user.role != 'petugas':
            raise PermissionDenied('Hanya petugas yang ditugaskan yang dapat memperbarui status ini.')
        if instance.petugas_id != user.pk:
            raise PermissionDenied('Petugas hanya dapat memperbarui penjemputan yang ditugaskan kepadanya.')
        return

    raise InvalidStatusTransitionError(
        f"Tidak dapat mengubah status dari '{current_status}' ke '{new_status}'."
    )
