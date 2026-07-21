from ..models import Notifikasi, User


def create_notification(
    user_id: int,
    judul: str,
    deskripsi: str,
    kategori: str = 'sistem',
) -> Notifikasi:
    """Create an in-app notification and trigger FCM (failsafe)."""
    notif = Notifikasi.objects.create(
        user_id=user_id,
        judul=judul,
        deskripsi=deskripsi,
        kategori=kategori,
    )
    try:
        from api.services.fcm import trigger_fcm_for_notification
        trigger_fcm_for_notification(notif)
    except Exception as exc:
        import logging
        logging.getLogger('miru.request').error(
            'Gagal trigger FCM setelah notifikasi: %s', exc,
        )
    return notif


def broadcast_notification(
    judul: str,
    deskripsi: str,
    kategori: str = 'pengumuman',
    *,
    pengumuman_id: int | None = None,
) -> int:
    """
    Buat Notifikasi in-app + FCM untuk semua nasabah aktif.

    Digunakan untuk pengumuman umum dan perubahan harga.
    Returns jumlah Notifikasi yang dibuat.
    """
    nasabah_ids = list(
        User.objects.filter(role='nasabah', is_active=True)
        .values_list('id', flat=True)
    )
    if not nasabah_ids:
        return 0

    notifs = [
        Notifikasi(
            user_id=uid,
            judul=judul,
            deskripsi=deskripsi,
            kategori=kategori,
        )
        for uid in nasabah_ids
    ]
    created = Notifikasi.objects.bulk_create(notifs)

    # FCM ke semua device token nasabah (failsafe)
    try:
        from api.services.fcm import build_notification_payload, send_to_user_ids
        send_to_user_ids(
            nasabah_ids,
            title=judul,
            body=deskripsi,
            data=build_notification_payload(
                kategori=kategori,
                pengumuman_id=pengumuman_id,
                event=kategori,
            ),
        )
    except Exception as exc:
        import logging
        logging.getLogger('miru.request').error(
            'Gagal broadcast FCM (%s): %s', kategori, exc,
        )

    return len(created)


def trigger_email_new_pickup(pickup) -> None:
    """Kirim email ke admin untuk penjemputan baru (failsafe)."""
    try:
        from api.services.email_service import notify_admin_new_pickup
        notify_admin_new_pickup(pickup)
    except Exception as exc:
        import logging
        logger = logging.getLogger('miru.request')
        logger.error('Gagal trigger email penjemputan: %s', exc)
