"""Price change history for waste categories."""

from decimal import Decimal

from api.middleware import get_current_user
from api.models import KategoriSampah, RiwayatHarga, User


def record_price_change(
    kategori: KategoriSampah,
    harga_lama: Decimal,
    harga_baru: Decimal,
    user: User | None = None,
) -> RiwayatHarga | None:
    """Record a price change when harga_beli_per_kg is updated."""
    if harga_lama == harga_baru:
        return None
    if user is None:
        user = get_current_user()
    return RiwayatHarga.objects.create(
        kategori=kategori,
        harga_lama=harga_lama,
        harga_baru=harga_baru,
        diubah_oleh=user if user and user.is_authenticated else None,
    )


def get_price_history(kategori_id: int):
    """Return price history queryset for a category."""
    return (
        RiwayatHarga.objects.filter(kategori_id=kategori_id)
        .select_related('diubah_oleh', 'kategori')
        .order_by('-tanggal_berlaku')
    )
