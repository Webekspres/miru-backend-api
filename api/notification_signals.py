"""Signal handlers for automatic Notifikasi generation.

Triggers on key business events:
- TransaksiSetoran: notifikasi dipanggil dari ledger SETELAH total_nilai di-set
  (bukan di sini — create awal masih total_nilai=0)
- Penjemputan status changed → "Status Penjemputan"
- PenarikanSaldo approved/rejected → "Penarikan Saldo"
- PenukaranPoin created → nasabah + admin; approved/rejected/cancelled → nasabah
- Pengaduan gets tindak_lanjut → "Tindak Lanjut Pengaduan"
"""

from django.db.models.signals import post_save

from .models import (
    Pengaduan,
    PenarikanSaldo,
    Pengumuman,
    Penjemputan,
    PenukaranPoin,
    User,
)
from .services.notifications import (
    broadcast_notification,
    create_notification,
    notify_admins,
    notify_roles,
    trigger_email_new_pickup,
)


# ──────────────────────────────────────────────
# Handlers
# ──────────────────────────────────────────────


# ──────────────────────────────────────────────
# Handlers
# ──────────────────────────────────────────────


def _notif_penjemputan(instance, created, **kwargs):
    if created:
        # Kirim email ke admin untuk penjemputan baru
        trigger_email_new_pickup(instance)
        create_notification(
            user_id=instance.nasabah_id,
            judul='Pengajuan Penjemputan Diterima',
            deskripsi=(
                'Pengajuan penjemputan sampah Anda telah diterima. '
                'Menunggu persetujuan admin MIRU.'
            ),
            kategori='penjemputan',
        )
        # In-app ke admin/koordinator — segera tindak lanjuti
        notify_roles(
            ('admin', 'koordinator'),
            judul='Penjemputan Baru',
            deskripsi=(
                f'Ada pengajuan penjemputan baru (ID {instance.id}). '
                f'Segera tindak lanjuti. Alamat: {instance.alamat_jemput}.'
            ),
            kategori='penjemputan',
        )
        return

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
            'judul': 'Penjemputan Akan Dijemput',
            'deskripsi': _nasabah_dijadwalkan_deskripsi(instance),
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

    # Saat admin menugaskan petugas → notifikasi ke petugas
    if instance.status == 'dijadwalkan' and instance.petugas_id:
        create_notification(
            user_id=instance.petugas_id,
            judul='Tugas Penjemputan Baru',
            deskripsi=_petugas_tugas_deskripsi(instance),
            kategori='penjemputan',
        )

    # Saat selesai → notifikasi ke petugas + admin
    if instance.status == 'selesai':
        selesai_deskripsi = (
            f'Penjemputan ID {instance.id} telah selesai. '
            f'Alamat: {instance.alamat_jemput}.'
        )
        if instance.petugas_id:
            create_notification(
                user_id=instance.petugas_id,
                judul='Penjemputan Selesai',
                deskripsi=selesai_deskripsi,
                kategori='penjemputan',
            )
        notify_roles(
            ('admin',),
            judul='Penjemputan Selesai',
            deskripsi=selesai_deskripsi,
            kategori='penjemputan',
            exclude_user_ids={instance.petugas_id} if instance.petugas_id else None,
        )


def _nasabah_dijadwalkan_deskripsi(instance: Penjemputan) -> str:
    petugas_nama = ''
    if instance.petugas_id:
        petugas = getattr(instance, 'petugas', None)
        if petugas is not None and getattr(petugas, 'nama_lengkap', None):
            petugas_nama = petugas.nama_lengkap
        else:
            from .models import User
            petugas_nama = (
                User.objects.filter(pk=instance.petugas_id)
                .values_list('nama_lengkap', flat=True)
                .first()
                or ''
            )

    if petugas_nama:
        return (
            f'Sampah Anda sudah disetujui dan akan dijemput oleh petugas kami '
            f'({petugas_nama}). '
            f'Jadwal: {instance.jadwal.strftime("%d %b %Y, %H:%M")} WIT. '
            f'Mohon siapkan sampah Anda.'
        )
    return (
        'Sampah Anda sudah disetujui dan akan dijemput oleh petugas kami. '
        f'Jadwal: {instance.jadwal.strftime("%d %b %Y, %H:%M")} WIT. '
        f'Mohon siapkan sampah Anda.'
    )


def _petugas_tugas_deskripsi(instance: Penjemputan) -> str:
    nasabah_nama = ''
    nasabah = getattr(instance, 'nasabah', None)
    if nasabah is not None and getattr(nasabah, 'nama_lengkap', None):
        nasabah_nama = nasabah.nama_lengkap
    else:
        from .models import User
        nasabah_nama = (
            User.objects.filter(pk=instance.nasabah_id)
            .values_list('nama_lengkap', flat=True)
            .first()
            or 'nasabah'
        )

    return (
        f'Anda mendapat tugas menjemput sampah. '
        f'Nasabah: {nasabah_nama}. '
        f'Alamat: {instance.alamat_jemput}. '
        f'Jadwal: {instance.jadwal.strftime("%d %b %Y, %H:%M")} WIT.'
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
        nasabah_nama = ''
        nasabah = getattr(instance, 'nasabah', None)
        if nasabah is not None and getattr(nasabah, 'nama_lengkap', None):
            nasabah_nama = nasabah.nama_lengkap
        else:
            nasabah_nama = (
                User.objects.filter(pk=instance.nasabah_id)
                .values_list('nama_lengkap', flat=True)
                .first()
                or 'Nasabah'
            )
        notify_roles(
            ('admin',),
            judul='Pengajuan Penukaran Poin Baru',
            deskripsi=(
                f'{nasabah_nama} mengajukan penukaran {reward_nama} '
                f'({instance.poin_dibutuhkan} poin).'
            ),
            kategori='penukaran',
        )
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status is None or old_status == instance.status:
        return

    reward_nama = instance.reward.nama if instance.reward else 'Reward'

    if instance.status == 'selesai':
        create_notification(
            user_id=instance.nasabah_id,
            judul='Penukaran Poin Berhasil',
            deskripsi=(
                f'Selamat! Penukaran poin untuk {reward_nama} telah disetujui. '
                f'Hubungi admin MIRU untuk pengambilan reward.'
            ),
            kategori='penukaran',
        )
    elif instance.status == 'ditolak':
        create_notification(
            user_id=instance.nasabah_id,
            judul='Penukaran Poin Ditolak',
            deskripsi=(
                f'Mohon maaf, penukaran poin untuk {reward_nama} ditolak. '
                f'Hubungi admin MIRU untuk informasi lebih lanjut.'
            ),
            kategori='penukaran',
        )
    elif instance.status == 'dibatalkan':
        create_notification(
            user_id=instance.nasabah_id,
            judul='Penukaran Poin Dibatalkan',
            deskripsi=(
                f'Penukaran poin untuk {reward_nama} telah dibatalkan.'
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
        nasabah_nama = ''
        nasabah = getattr(instance, 'nasabah', None)
        if nasabah is not None and getattr(nasabah, 'nama_lengkap', None):
            nasabah_nama = nasabah.nama_lengkap
        notify_admins(
            judul='Pengaduan Baru',
            deskripsi=(
                f'Pengaduan baru dari {nasabah_nama or "nasabah"}: '
                f'"{instance.get_jenis_pengaduan_display()}". '
                f'Silakan ditindaklanjuti.'
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


def _notif_pengumuman(instance, created, **kwargs):
    """Broadcast FCM + in-app saat pengumuman baru aktif (termasuk harga H-3)."""
    if not created or not instance.aktif:
        return

    # Auto-pengumuman harga memakai judul "Perubahan Harga …"
    kategori = (
        'harga'
        if instance.judul.startswith('Perubahan Harga')
        else 'pengumuman'
    )
    # Truncate body untuk FCM display (full isi tetap di model Pengumuman)
    deskripsi = instance.isi[:500]
    broadcast_notification(
        judul=instance.judul,
        deskripsi=deskripsi,
        kategori=kategori,
        pengumuman_id=instance.id,
    )


# ──────────────────────────────────────────────
# Connection helpers
# ──────────────────────────────────────────────


def connect_notification_signals():
    """Connect all notification signal handlers."""
    post_save.connect(_notif_penjemputan, sender=Penjemputan, weak=False)
    post_save.connect(_notif_penarikan, sender=PenarikanSaldo, weak=False)
    post_save.connect(_notif_penukaran, sender=PenukaranPoin, weak=False)
    post_save.connect(_notif_pengaduan, sender=Pengaduan, weak=False)
    post_save.connect(_notif_pengumuman, sender=Pengumuman, weak=False)


def disconnect_notification_signals():
    """Disconnect notification signal handlers."""
    post_save.disconnect(_notif_penjemputan, sender=Penjemputan)
    post_save.disconnect(_notif_penarikan, sender=PenarikanSaldo)
    post_save.disconnect(_notif_penukaran, sender=PenukaranPoin)
    post_save.disconnect(_notif_pengaduan, sender=Pengaduan)
    post_save.disconnect(_notif_pengumuman, sender=Pengumuman)
