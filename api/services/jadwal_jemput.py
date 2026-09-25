"""Jadwal jemput per wilayah (aturan klien: "terjadwal 2x seminggu per wilayah").

- Admin/koordinator menetapkan maks 2 hari jemput per wilayah per minggu
  (Senin–Minggu WIT); harinya bebas.
- Saat jadwal dibuat, nasabah aktif di wilayah itu mendapat notifikasi.
- Nasabah mengajukan jemput dengan memilih salah satu jadwal wilayahnya,
  paling lambat H-1 (sebelum tanggal jadwal, kalender WIT).
"""

from datetime import date, datetime, timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from api.models import JadwalJemputWilayah, Penjemputan, User, WilayahLayanan
from api.services.pickups import WIT, week_bounds_wit

MAX_JADWAL_PER_MINGGU = 2

# Pesanan yang masih berlaku (ditolak tidak dihitung).
ACTIVE_PICKUP_STATUSES = (
    'menunggu', 'disetujui', 'dijadwalkan', 'dalam_perjalanan', 'dijemput', 'selesai',
)

_HARI = ('Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu')
_BULAN = (
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
    'Agustus', 'September', 'Oktober', 'November', 'Desember',
)


def today_wit() -> date:
    return timezone.localtime(timezone.now(), WIT).date()


def format_tanggal_id(d: date) -> str:
    """Contoh: 'Selasa, 29 September 2026'."""
    return f'{_HARI[d.weekday()]}, {d.day} {_BULAN[d.month - 1]} {d.year}'


def format_jam(jadwal: JadwalJemputWilayah) -> str:
    return f"{jadwal.jam_mulai:%H.%M}–{jadwal.jam_selesai:%H.%M} WIT"


def jadwal_datetime(jadwal: JadwalJemputWilayah) -> datetime:
    """Waktu mulai jadwal sebagai datetime aware (WIT) untuk Penjemputan.jadwal."""
    return datetime.combine(jadwal.tanggal, jadwal.jam_mulai, tzinfo=WIT)


def is_bookable(jadwal: JadwalJemputWilayah) -> bool:
    """Pemesanan minimal H-1: hari ini (WIT) harus sebelum tanggal jadwal."""
    return today_wit() < jadwal.tanggal


def wilayah_label(wilayah: WilayahLayanan) -> str:
    return str(wilayah)


def validate_new_jadwal(wilayah: WilayahLayanan, tanggal: date, jam_mulai, jam_selesai) -> None:
    if not wilayah.aktif:
        raise ValidationError({'wilayah': ['Wilayah tidak aktif untuk layanan penjemputan.']})
    if tanggal <= today_wit():
        raise ValidationError({
            'tanggal': ['Jadwal minimal untuk besok agar warga sempat memesan (H-1).'],
        })
    if jam_selesai <= jam_mulai:
        raise ValidationError({'jam_selesai': ['Jam selesai harus setelah jam mulai.']})
    if JadwalJemputWilayah.objects.filter(wilayah=wilayah, tanggal=tanggal).exists():
        raise ValidationError({
            'tanggal': ['Wilayah ini sudah punya jadwal jemput pada tanggal tersebut.'],
        })

    ref = datetime.combine(tanggal, jam_mulai, tzinfo=WIT)
    start, end = week_bounds_wit(ref)
    count = JadwalJemputWilayah.objects.filter(
        wilayah=wilayah, tanggal__gte=start.date(), tanggal__lt=end.date(),
    ).count()
    if count >= MAX_JADWAL_PER_MINGGU:
        raise ValidationError({
            'tanggal': [
                f'Maksimal {MAX_JADWAL_PER_MINGGU} jadwal jemput per minggu per wilayah. '
                f'Minggu {start.date():%d/%m}–{(end - timedelta(days=1)).date():%d/%m} '
                f'sudah penuh untuk {wilayah_label(wilayah)}.'
            ],
        })


def notify_jadwal_baru(jadwal: JadwalJemputWilayah) -> int:
    """Notifikasi in-app + FCM ke nasabah aktif di wilayah jadwal."""
    from api.models import Notifikasi

    nasabah_ids = list(
        User.objects.filter(
            role='nasabah', is_active=True, kelurahan_id=jadwal.wilayah_id,
        ).values_list('id', flat=True)
    )
    if not nasabah_ids:
        return 0

    judul = 'Jadwal penjemputan baru'
    deskripsi = (
        f'Ada jadwal penjemputan di {wilayah_label(jadwal.wilayah)} pada '
        f'{format_tanggal_id(jadwal.tanggal)} pukul {format_jam(jadwal)}. '
        f'Segera jadwalkan penjemputan Anda.'
    )
    Notifikasi.objects.bulk_create([
        Notifikasi(user_id=uid, judul=judul, deskripsi=deskripsi, kategori='jadwal_jemput')
        for uid in nasabah_ids
    ])
    try:
        from api.services.fcm import build_notification_payload, send_to_user_ids
        send_to_user_ids(
            nasabah_ids,
            title=judul,
            body=deskripsi,
            data=build_notification_payload(kategori='jadwal_jemput', event='jadwal_jemput'),
        )
    except Exception as exc:
        import logging
        logging.getLogger('miru.request').error('Gagal FCM jadwal jemput: %s', exc)
    return len(nasabah_ids)


@transaction.atomic
def create_jadwal(*, wilayah, tanggal, jam_mulai, jam_selesai, catatan='', dibuat_oleh=None):
    # Kunci baris wilayah agar dua admin tidak melewati batas 2/minggu bersamaan.
    WilayahLayanan.objects.select_for_update().filter(pk=wilayah.pk).first()
    validate_new_jadwal(wilayah, tanggal, jam_mulai, jam_selesai)
    jadwal = JadwalJemputWilayah.objects.create(
        wilayah=wilayah, tanggal=tanggal, jam_mulai=jam_mulai,
        jam_selesai=jam_selesai, catatan=catatan, dibuat_oleh=dibuat_oleh,
    )
    transaction.on_commit(lambda: notify_jadwal_baru(jadwal))
    return jadwal


def validate_can_delete(jadwal: JadwalJemputWilayah) -> None:
    if jadwal.penjemputan.filter(status__in=ACTIVE_PICKUP_STATUSES).exists():
        raise ValidationError({
            'non_field_errors': [
                'Jadwal tidak dapat dihapus karena sudah ada pesanan penjemputan. '
                'Tolak pesanan terkait terlebih dahulu.'
            ],
        })


def validate_booking(nasabah: User, jadwal: JadwalJemputWilayah) -> None:
    """Validasi nasabah memesan jadwal wilayahnya sendiri, H-1, tanpa dobel."""
    if nasabah.kelurahan_id is None:
        raise ValidationError({
            'jadwal_wilayah': [
                'Lengkapi kelurahan/kampung di profil Anda terlebih dahulu '
                'untuk melihat jadwal penjemputan.'
            ],
        })
    if jadwal.wilayah_id != nasabah.kelurahan_id:
        raise ValidationError({
            'jadwal_wilayah': ['Jadwal ini bukan untuk wilayah Anda.'],
        })
    if not jadwal.wilayah.aktif:
        raise ValidationError({
            'jadwal_wilayah': [
                'Maaf, wilayah Anda saat ini belum masuk dalam layanan '
                'penjemputan MIRU. Silakan hubungi admin untuk informasi lebih lanjut.'
            ],
        })
    if not is_bookable(jadwal):
        raise ValidationError({
            'jadwal_wilayah': [
                'Pemesanan untuk jadwal ini sudah ditutup (minimal H-1). '
                'Silakan pilih jadwal berikutnya.'
            ],
        })
    if Penjemputan.objects.filter(
        nasabah=nasabah, jadwal_wilayah=jadwal, status__in=ACTIVE_PICKUP_STATUSES,
    ).exists():
        raise ValidationError({
            'jadwal_wilayah': ['Anda sudah mengajukan penjemputan pada jadwal ini.'],
        })
