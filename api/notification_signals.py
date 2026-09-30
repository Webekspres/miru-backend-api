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
            judul='📦 Pengajuan penjemputan diterima',
            deskripsi=(
                'Terima kasih sudah peduli lingkungan! Pengajuan Anda sedang '
                'kami cek — kabar selanjutnya segera menyusul.'
            ),
            kategori='penjemputan',
        )
        # In-app ke admin/koordinator — segera tindak lanjuti
        notify_roles(
            ('admin', 'koordinator'),
            judul='Penjemputan Baru',
            deskripsi=(
                f'Ada pengajuan penjemputan baru (ID {instance.id}) di '
                f'{instance.alamat_jemput}. Yuk segera tindak lanjuti!'
            ),
            kategori='penjemputan',
        )
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status is None or old_status == instance.status:
        return

    status_messages = {
        'disetujui': {
            'judul': '👍 Kabar baik, penjemputan disetujui!',
            'deskripsi': 'Pengajuan Anda sudah disetujui. Petugas akan segera '
                         'dijadwalkan untuk menjemput sampah Anda.',
        },
        'dijadwalkan': {
            'judul': '🗓️ Siap-siap, sampah Anda akan dijemput',
            'deskripsi': _nasabah_dijadwalkan_deskripsi(instance),
        },
        'dalam_perjalanan': {
            'judul': '🚚 Petugas dalam perjalanan ke rumah Anda',
            'deskripsi': 'Bersiap ya! Letakkan sampah yang sudah dipilah di depan '
                         'rumah supaya penjemputan lebih cepat.',
        },
        'dijemput': {
            'judul': '♻️ Sampah Anda sedang dijemput',
            'deskripsi': 'Petugas sudah tiba dan sedang menimbang sampah Anda. '
                         'Terima kasih sudah memilah dengan baik!',
        },
        'selesai': {
            'judul': '🎉 Selamat! Penjemputan selesai',
            'deskripsi': _nasabah_selesai_deskripsi(instance),
        },
        'ditolak': {
            'judul': '😔 Penjemputan belum bisa diproses',
            'deskripsi': 'Mohon maaf, pengajuan penjemputan Anda ditolak. Jangan '
                         'berkecil hati — hubungi admin MIRU atau ajukan lagi di '
                         'jadwal berikutnya.',
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
            judul='🧹 Tugas penjemputan baru',
            deskripsi=_petugas_tugas_deskripsi(instance),
            kategori='penjemputan',
        )

    # Saat selesai → notifikasi ke petugas + admin
    if instance.status == 'selesai':
        total = _setoran_total_fmt(instance)
        selesai_deskripsi = (
            f'Kerja bagus! Penjemputan ID {instance.id} di {instance.alamat_jemput} '
            f'selesai' + (f' dengan setoran Rp{total}.' if total else '.')
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


def _rupiah(nilai) -> str:
    """12000 → 'Rp12.000' (format Indonesia)."""
    return 'Rp' + f'{nilai:,.0f}'.replace(',', '.')


def _setoran_total_fmt(instance: Penjemputan) -> str:
    """Nilai setoran hasil timbang (mis. '12.000'), kosong bila belum ada."""
    setoran = getattr(instance, 'setoran', None) if instance.setoran_id else None
    if setoran is None or not setoran.total_nilai:
        return ''
    return f'{setoran.total_nilai:,.0f}'.replace(',', '.')


def _nasabah_selesai_deskripsi(instance: Penjemputan) -> str:
    total = _setoran_total_fmt(instance)
    if total:
        return (
            f'Hasil timbang Rp{total} sudah masuk ke saldo Anda. Terima kasih '
            f'telah ikut menjaga Mimika tetap bersih! 💚'
        )
    return 'Terima kasih telah ikut menjaga Mimika tetap bersih! 💚'


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
            f'({petugas_nama}) pada {instance.jadwal.strftime("%d %b %Y, %H:%M")} WIT. '
            f'Yuk siapkan sampahnya dan pastikan sudah terpilah!'
        )
    return (
        'Sampah Anda sudah disetujui dan akan dijemput oleh petugas kami pada '
        f'{instance.jadwal.strftime("%d %b %Y, %H:%M")} WIT. '
        f'Yuk siapkan sampahnya dan pastikan sudah terpilah!'
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
        f'Anda mendapat tugas menjemput sampah {nasabah_nama} di '
        f'{instance.alamat_jemput}, {instance.jadwal.strftime("%d %b %Y, %H:%M")} WIT. '
        f'Semangat bertugas! 💪'
    )


def _notif_penarikan(instance, created, **kwargs):
    if created:
        create_notification(
            user_id=instance.nasabah_id,
            judul='💸 Penarikan saldo diajukan',
            deskripsi=(
                f'Pengajuan penarikan {_rupiah(instance.nominal)} sudah kami terima '
                f'dan akan diproses dalam 1–2 hari kerja.'
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
            judul='✅ Penarikan saldo disetujui',
            deskripsi=(
                f'Hasil memilah sampah Anda siap dinikmati! {_rupiah(instance.nominal)} '
                f'bisa diambil tunai di kantor MIRU. 🙌'
            ),
            kategori='penarikan',
        )
    elif instance.status == 'ditolak':
        create_notification(
            user_id=instance.nasabah_id,
            judul='😔 Penarikan saldo belum disetujui',
            deskripsi=(
                f'Mohon maaf, penarikan {_rupiah(instance.nominal)} ditolak dan saldo '
                f'Anda tetap utuh. Hubungi admin MIRU untuk informasi lebih lanjut.'
            ),
            kategori='penarikan',
        )


def _notif_penukaran(instance, created, **kwargs):
    if created:
        reward_nama = instance.reward.nama if instance.reward else 'Reward'
        create_notification(
            user_id=instance.nasabah_id,
            judul='🎁 Penukaran poin diajukan',
            deskripsi=(
                f'Penukaran {reward_nama} sedang menunggu persetujuan admin. '
                f'Sebentar lagi hadiahnya!'
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
            judul='🎉 Selamat! Penukaran poin berhasil',
            deskripsi=(
                f'{reward_nama} siap untuk Anda. Hubungi admin MIRU untuk '
                f'mengambil hadiahnya — terima kasih sudah rajin menabung sampah!'
            ),
            kategori='penukaran',
        )
    elif instance.status == 'ditolak':
        create_notification(
            user_id=instance.nasabah_id,
            judul='😔 Penukaran poin belum disetujui',
            deskripsi=(
                f'Mohon maaf, penukaran {reward_nama} ditolak. Hubungi admin MIRU '
                f'untuk informasi lebih lanjut.'
            ),
            kategori='penukaran',
        )
    elif instance.status == 'dibatalkan':
        create_notification(
            user_id=instance.nasabah_id,
            judul='Penukaran poin dibatalkan',
            deskripsi=(
                f'Penukaran {reward_nama} dibatalkan. Masih banyak hadiah lain '
                f'yang bisa Anda pilih!'
            ),
            kategori='penukaran',
        )


def _notif_pengaduan(instance, created, **kwargs):
    if created:
        create_notification(
            user_id=instance.nasabah_id,
            judul='📨 Pengaduan Anda kami terima',
            deskripsi=(
                f'Terima kasih sudah memberi tahu kami soal '
                f'"{instance.get_jenis_pengaduan_display()}". Admin akan '
                f'menindaklanjuti maksimal 2 hari kerja.'
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
        judul='✅ Pengaduan sudah ditindaklanjuti',
        deskripsi=(
            f'Pengaduan "{instance.get_jenis_pengaduan_display()}" sudah ditangani '
            f'admin. Lihat detailnya di menu Pengaduan — terima kasih atas masukannya!'
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
