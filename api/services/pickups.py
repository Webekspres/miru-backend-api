"""Pickup request validation and status state machine.

Fase 8.3 — Wilayah layanan & kuota penjemputan:
- Validasi penjemputan hanya di wilayah terdaftar
- Validasi frekuensi max 2x seminggu per wilayah
"""

from datetime import timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.db.models import Count
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from api.exceptions import InvalidStatusTransitionError
from api.models import Penjemputan, User, WilayahLayanan

MIN_ESTIMASI_BERAT_KG = Decimal('5')
MAX_PICKUPS_PER_WEEK_PER_WILAYAH = 2
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


def validate_wilayah_layanan(nasabah: User) -> None:
    """Validasi nasabah berada di wilayah layanan aktif."""
    if nasabah.kelurahan_id is None:
        # Wilayah tidak diisi — lewati validasi (backward compat)
        return
    try:
        wilayah = WilayahLayanan.objects.get(pk=nasabah.kelurahan_id)
    except WilayahLayanan.DoesNotExist:
        raise ValidationError('Wilayah tidak terdaftar.')
    if not wilayah.aktif:
        raise ValidationError(
            'Maaf, wilayah Anda saat ini belum masuk dalam layanan '
            'penjemputan MIRU. Silakan hubungi admin untuk informasi lebih lanjut.'
        )


def validate_max_pickups_per_week(nasabah: User) -> None:
    """Validasi max 2x penjemputan per minggu per wilayah.

    Menggunakan kelurahan_id sebagai identifikasi wilayah.
    Jika nasabah tidak punya kelurahan, lewati validasi.
    """
    if nasabah.kelurahan_id is None:
        return

    now = timezone.now()
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    count_this_week = (
        Penjemputan.objects
        .filter(
            nasabah__kelurahan_id=nasabah.kelurahan_id,
            jadwal__gte=start_of_week,
            status__in=['menunggu', 'disetujui', 'dijadwalkan', 'dalam_perjalanan', 'dijemput', 'selesai'],
        )
        .exclude(status='ditolak')
        .count()
    )

    if count_this_week >= MAX_PICKUPS_PER_WEEK_PER_WILAYAH:
        raise ValidationError(
            f'Maksimal {MAX_PICKUPS_PER_WEEK_PER_WILAYAH}x penjemputan '
            f'per minggu per wilayah. '
            f'Minggu ini sudah ada {count_this_week} penjemputan untuk wilayah ini.'
        )


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


def approve_pickup(instance: Penjemputan, user: User) -> Penjemputan:
    validate_status_transition(instance, 'disetujui', user)
    instance.status = 'disetujui'
    instance.save(update_fields=['status'])
    return instance


def reject_pickup(instance: Penjemputan, user: User) -> Penjemputan:
    validate_status_transition(instance, 'ditolak', user)
    instance.status = 'ditolak'
    instance.save(update_fields=['status'])
    return instance


def assign_pickup(instance: Penjemputan, user: User, petugas_id: int) -> Penjemputan:
    try:
        petugas = User.objects.get(pk=petugas_id)
    except User.DoesNotExist as exc:
        raise ValidationError({'petugas_id': ['Petugas tidak ditemukan.']}) from exc

    validate_petugas_user(petugas)
    validate_status_transition(instance, 'dijadwalkan', user, petugas=petugas)
    instance.petugas = petugas
    instance.status = 'dijadwalkan'
    instance.save(update_fields=['petugas', 'status'])
    return instance


def update_pickup_status(instance: Penjemputan, user: User, new_status: str) -> Penjemputan:
    validate_status_transition(instance, new_status, user)
    instance.status = new_status
    instance.save(update_fields=['status'])
    return instance
