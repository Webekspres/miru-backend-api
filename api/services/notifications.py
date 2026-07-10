from ..models import Notifikasi


def create_notification(
    user_id: int,
    judul: str,
    deskripsi: str,
    kategori: str = 'sistem',
) -> Notifikasi:
    """Create a notification for a user."""
    return Notifikasi.objects.create(
        user_id=user_id,
        judul=judul,
        deskripsi=deskripsi,
        kategori=kategori,
    )
