"""Pickup request validation and status state machine.

Fase 8.3 — Wilayah layanan & kuota penjemputan:
- Validasi penjemputan hanya di wilayah terdaftar
- Validasi frekuensi max 2x seminggu per wilayah

T3 — Alur approve+assign atomik, validasi jadwal, koordinat opsional.
"""

from datetime import timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from api.exceptions import InvalidStatusTransitionError
from api.models import PengaturanInstitusi, Penjemputan, User, WilayahLayanan

MIN_ESTIMASI_BERAT_KG = Decimal('5')
MAX_PICKUPS_PER_WEEK_PER_WILAYAH = 2
MIN_JADWAL_AHEAD = timedelta(hours=1)
WIT = ZoneInfo('Asia/Jayapura')

# Status aktif untuk antrian petugas (bukan menunggu/ditolak/selesai).
PETUGAS_VISIBLE_STATUSES = (
    'dijadwalkan',
    'dalam_perjalanan',
    'dijemput',
)

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    'menunggu': {'disetujui', 'dijadwalkan', 'ditolak'},
    'disetujui': {'dijadwalkan'},
    'dijadwalkan': {'dalam_perjalanan'},
    'dalam_perjalanan': {'dijemput'},
    'dijemput': {'selesai'},
    'selesai': set(),
    'ditolak': set(),
}

ADMIN_TRANSITIONS = {
    ('menunggu', 'disetujui'),
    ('menunggu', 'dijadwalkan'),
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
        raise ValidationError({'alamat_jemput': ['Wilayah tidak terdaftar.']})
    if not wilayah.aktif:
        raise ValidationError({
            'alamat_jemput': [
                'Maaf, wilayah Anda saat ini belum masuk dalam layanan '
                'penjemputan MIRU. Silakan hubungi admin untuk informasi lebih lanjut.'
            ],
        })


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
        raise ValidationError({
            'jadwal': [
                f'Maksimal {MAX_PICKUPS_PER_WEEK_PER_WILAYAH}x penjemputan '
                f'per minggu per wilayah. '
                f'Minggu ini sudah ada {count_this_week} penjemputan untuk wilayah ini.'
            ],
        })


def validate_estimasi_berat(berat: Decimal) -> Decimal:
    if berat < MIN_ESTIMASI_BERAT_KG:
        raise ValidationError('Minimal estimasi berat penjemputan 5 kg.')
    return berat


def validate_jadwal(jadwal) -> None:
    """Tolak jadwal di masa lalu; minimal ~1 jam dari sekarang (WIT)."""
    now = timezone.now()
    if timezone.is_naive(jadwal):
        jadwal_aware = timezone.make_aware(jadwal, WIT)
    else:
        jadwal_aware = jadwal

    if jadwal_aware <= now:
        raise ValidationError(
            {'jadwal': ['Jadwal penjemputan tidak boleh di masa lalu.']}
        )

    min_ahead = now + MIN_JADWAL_AHEAD
    if jadwal_aware < min_ahead:
        raise ValidationError(
            {'jadwal': ['Jadwal penjemputan minimal 1 jam dari sekarang.']}
        )


# Alias lama untuk kompatibilitas impor
validate_jadwal_h_plus_one = validate_jadwal


def is_di_luar_jam_layanan(jadwal) -> bool:
    """True jika waktu jadwal (WIT) di luar jam_buka–jam_tutup institusi."""
    settings = PengaturanInstitusi.load()
    if settings.jam_buka is None or settings.jam_tutup is None:
        return False

    if timezone.is_naive(jadwal):
        jadwal_wit = timezone.make_aware(jadwal, WIT)
    else:
        jadwal_wit = jadwal.astimezone(WIT)

    t = jadwal_wit.time()
    return t < settings.jam_buka or t > settings.jam_tutup


def out_of_hours_meta(jadwal) -> dict | None:
    """Meta peringatan jemput di luar jam layanan (tidak menolak create)."""
    if not is_di_luar_jam_layanan(jadwal):
        return None
    return {
        'di_luar_jam_layanan': True,
        'peringatan': (
            'Jadwal yang dipilih di luar jam operasional institusi. '
            'Pengajuan tetap diterima; petugas mungkin menyesuaikan jadwal.'
        ),
    }


def validate_koordinat(latitude, longitude) -> None:
    """Validasi rentang lat/lng jika diisi (bukan live tracking)."""
    if latitude is None and longitude is None:
        return
    if latitude is None or longitude is None:
        raise ValidationError(
            'Latitude dan longitude harus diisi bersamaan, atau keduanya dikosongkan.'
        )
    lat = Decimal(str(latitude))
    lng = Decimal(str(longitude))
    if lat < Decimal('-90') or lat > Decimal('90'):
        raise ValidationError({'latitude': ['Latitude harus antara -90 dan 90.']})
    if lng < Decimal('-180') or lng > Decimal('180'):
        raise ValidationError({'longitude': ['Longitude harus antara -180 dan 180.']})


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


def _require_assigned_petugas(
    instance: Penjemputan,
    petugas: User | None,
    *,
    field: str = 'petugas',
) -> User:
    assigned = petugas if petugas is not None else instance.petugas
    if assigned is None:
        raise ValidationError({
            field: ['Petugas wajib ditugaskan. Tidak boleh menyetujui tanpa petugas.'],
        })
    return validate_petugas_user(assigned)


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
        if new_status in ('disetujui', 'dijadwalkan'):
            _require_assigned_petugas(instance, petugas)
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


@transaction.atomic
def approve_pickup(instance: Penjemputan, user: User, petugas_id: int) -> Penjemputan:
    """Setujui + assign atomik: menunggu → dijadwalkan dengan petugas."""
    try:
        petugas = User.objects.select_for_update().get(pk=petugas_id)
    except User.DoesNotExist as exc:
        raise ValidationError({'petugas_id': ['Petugas tidak ditemukan.']}) from exc

    validate_petugas_user(petugas)
    validate_status_transition(instance, 'dijadwalkan', user, petugas=petugas)
    instance.petugas = petugas
    instance.status = 'dijadwalkan'
    instance.save(update_fields=['petugas', 'status'])
    return instance


def reject_pickup(instance: Penjemputan, user: User) -> Penjemputan:
    validate_status_transition(instance, 'ditolak', user)
    instance.status = 'ditolak'
    instance.save(update_fields=['status'])
    return instance


def assign_pickup(instance: Penjemputan, user: User, petugas_id: int) -> Penjemputan:
    return approve_pickup(instance, user, petugas_id)


def update_pickup_status(instance: Penjemputan, user: User, new_status: str) -> Penjemputan:
    validate_status_transition(instance, new_status, user)
    instance.status = new_status
    instance.save(update_fields=['status'])
    return instance
