"""Signal handlers for automatic Notifikasi generation.

Triggers on key business events:
- TransaksiSetoran created → "Setoran Baru"
- Penjemputan status changed → "Status Penjemputan"
- PenarikanSaldo approved/rejected → "Penarikan Saldo"
- PenukaranPoin approved → "Penukaran Poin"
- Pengaduan gets tindak_lanjut → "Tindak Lanjut Pengaduan"
"""

from django.db.models.signals import post_save

from .models import (
    Pengaduan,
    PenarikanSaldo,
    Penjemputan,
    PenukaranPoin,
    TransaksiSetoran,
)
from .services.notifications import create_notification


# ──────────────────────────────────────────────
# Handlers
# ──────────────────────────────────────────────


def _notif_setoran(instance, created, **kwargs):
    if not created:
        return
    nasabah = instance.nasabah
    if not nasabah:
        return
    create_notification(
        user_id=nasabah.id,
        judul='Setoran Sampah Berhasil',
        deskripsi=(
            f'Setoran sampah sebesar Rp{instance.total_nilai:,.0f} '
            f'telah dicatat ke akun Anda. Cek saldo di halaman utama.'
        ),
        kategori='setoran',
    )


def _notif_penjemputan(instance, created, **kwargs):
    if created:
        return  # Only status changes trigger notifications

    old_status = getattr(instance, '_old_status', None)
    if old_status is None or old_status == instance.status:
        return

    status_messages = {
        'disetujui': {
            'judul': 'Penjemputan Disetujui',
            'deskripsi': 'Penjemputan sampah Anda telah disetujui. '
                          'Petugas akan segera dijadwalkan.',
        },
        'dijadwalkan': {
            'judul': 'Penjemputan Dijadwalkan',
            'deskripsi': (
                f'Penjemputan sampah Anda telah dijadwalkan '
                f'pada {instance.jadwal.strftime("%d %b %Y, %H:%M")} WIT. '
                f'Mohon siapkan sampah Anda.'
            ),
        },
        'dalam_perjalanan': {
            'judul': 'Petugas Dalam Perjalanan',
            'deskripsi': 'Petugas MIRU sedang dalam perjalanan ke '
                         'lokasi Anda untuk menjemput sampah.',
        },
        'dijemput': {
            'judul': 'Sampah Sedang Dijemput',
            'deskripsi': 'Petugas sedang melakukan penjemputan sampah di lokasi Anda.',
        },
        'selesai': {
            'judul': 'Penjemputan Selesai',
            'deskripsi': 'Penjemputan sampah Anda telah selesai. '
                         'Saldo akan bertambah setelah setoran dicatat.',
        },
        'ditolak': {
            'judul': 'Penjemputan Ditolak',
            'deskripsi': 'Mohon maaf, penjemputan sampah Anda ditolak. '
                         'Hubungi admin MIRU untuk informasi lebih lanjut.',
        },
    }

    msg = status_messages.get(instance.status)
    if msg is None:
        return

    create_notification(
        user_id=instance.nasabah_id,
        judul=msg['judul'],
        deskripsi=msg['deskripsi'],
        kategori='penjemputan',
    )


def _notif_penarikan(instance, created, **kwargs):
    if created:
        create_notification(
            user_id=instance.nasabah_id,
            judul='Penarikan Saldo Diajukan',
            deskripsi=(
                f'Pengajuan penarikan saldo sebesar '
                f'Rp{instance.nominal:,.0f} telah diterima. '
                f'Tunggu proses persetujuan admin (1-2 hari kerja).'
            ),
            kategori='penarikan',
        )
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status is None or old_status == instance.status:
        return

    if instance.status == 'selesai':
        create_notification(
            user_id=instance.nasabah_id,
            judul='Penarikan Saldo Disetujui',
            deskripsi=(
                f'Penarikan saldo sebesar Rp{instance.nominal:,.0f} telah disetujui. '
                f'Saldo Anda telah terpotong. Silakan ambil tunai di kantor MIRU.'
            ),
            kategori='penarikan',
        )
    elif instance.status == 'ditolak':
        create_notification(
            user_id=instance.nasabah_id,
            judul='Penarikan Saldo Ditolak',
            deskripsi=(
                f'Mohon maaf, penarikan saldo sebesar '
                f'Rp{instance.nominal:,.0f} ditolak. '
                f'Hubungi admin MIRU untuk informasi lebih lanjut.'
            ),
            kategori='penarikan',
        )


def _notif_penukaran(instance, created, **kwargs):
    if created:
        reward_nama = instance.reward.nama if instance.reward else 'Reward'
        create_notification(
            user_id=instance.nasabah_id,
            judul='Penukaran Poin Diajukan',
            deskripsi=(
                f'Penukaran poin untuk {reward_nama} telah diajukan. '
                f'Tunggu persetujuan admin.'
            ),
            kategori='penukaran',
        )
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status is None or old_status == instance.status:
        return

    if instance.status != 'selesai':
        return

    reward_nama = instance.reward.nama if instance.reward else 'Reward'
    create_notification(
        user_id=instance.nasabah_id,
        judul='Penukaran Poin Berhasil',
        deskripsi=(
            f'Selamat! Penukaran poin untuk {reward_nama} telah disetujui. '
            f'Hubungi admin MIRU untuk pengambilan reward.'
        ),
        kategori='penukaran',
    )


def _notif_pengaduan(instance, created, **kwargs):
    if created:
        create_notification(
            user_id=instance.nasabah_id,
            judul='Pengaduan Diterima',
            deskripsi=(
                f'Pengaduan "{instance.get_jenis_pengaduan_display()}" telah diterima. '
                f'Admin akan menindaklanjuti maksimal 2 hari kerja.'
            ),
            kategori='pengaduan',
        )
        return

    # Only notify if admin added tindak_lanjut and status changed to ditutup
    if not instance.tindak_lanjut:
        return
    if instance.status != 'ditutup':
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status == instance.status:
        return  # No actual change

    create_notification(
        user_id=instance.nasabah_id,
        judul='Pengaduan Telah Ditindaklanjuti',
        deskripsi=(
            f'Pengaduan "{instance.get_jenis_pengaduan_display()}" telah '
            f'ditindaklanjuti oleh admin. Lihat detail di menu Pengaduan.'
        ),
        kategori='pengaduan',
    )


# ──────────────────────────────────────────────
# Connection helpers
# ──────────────────────────────────────────────


def connect_notification_signals():
    """Connect all notification signal handlers."""
    post_save.connect(_notif_setoran, sender=TransaksiSetoran, weak=False)
    post_save.connect(_notif_penjemputan, sender=Penjemputan, weak=False)
    post_save.connect(_notif_penarikan, sender=PenarikanSaldo, weak=False)
    post_save.connect(_notif_penukaran, sender=PenukaranPoin, weak=False)
    post_save.connect(_notif_pengaduan, sender=Pengaduan, weak=False)


def disconnect_notification_signals():
    """Disconnect notification signal handlers."""
    post_save.disconnect(_notif_setoran, sender=TransaksiSetoran)
    post_save.disconnect(_notif_penjemputan, sender=Penjemputan)
    post_save.disconnect(_notif_penarikan, sender=PenarikanSaldo)
    post_save.disconnect(_notif_penukaran, sender=PenukaranPoin)
    post_save.disconnect(_notif_pengaduan, sender=Pengaduan)
