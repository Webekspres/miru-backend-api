"""Price change history for waste categories.

Fase 8.2 — Kebijakan perubahan harga H-3:
- `tanggal_berlaku` wajib minimal H+3 dari saat penetapan
- Auto-buat pengumuman perubahan harga ke nasabah
- Auto-apply harga efektif saat transaksi
"""

from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from api.middleware import get_current_user
from api.models import KategoriSampah, Pengumuman, RiwayatHarga, User


H3_MINIMUM_HOURS = 72  # 3 * 24


def validate_tanggal_berlaku(tanggal_berlaku, ref_time=None):
    """Validasi tanggal_berlaku minimal H+3 dari ref_time (default: now)."""
    if ref_time is None:
        ref_time = timezone.now()
    min_date = ref_time + timedelta(hours=H3_MINIMUM_HOURS)
    if tanggal_berlaku < min_date:
        raise ValueError(
            f'tanggal_berlaku minimal {H3_MINIMUM_HOURS // 24} hari '
            f'({H3_MINIMUM_HOURS} jam) dari saat penetapan. '
            f'Tanggal yang diinput: {tanggal_berlaku.strftime("%Y-%m-%d %H:%M")}. '
            f'Minimal: {min_date.strftime("%Y-%m-%d %H:%M")}.'
        )


def _auto_create_pengumuman(kategori, harga_lama, harga_baru, tanggal_berlaku):
    """Buat pengumuman otomatis saat harga berubah."""
    judul = f'Perubahan Harga {kategori.nama}'
    isi = (
        f'Diberitahukan kepada seluruh nasabah, bahwa harga '
        f'{kategori.nama} akan berubah dari Rp{int(harga_lama):,} '
        f'menjadi Rp{int(harga_baru):,} per kg. '
        f'Perubahan ini mulai berlaku pada '
        f'{tanggal_berlaku.strftime("%d %B %Y %H:%M WIT")}.'
    )
    Pengumuman.objects.create(judul=judul, isi=isi, aktif=True)


def record_price_change(
    kategori: KategoriSampah,
    harga_lama: Decimal,
    harga_baru: Decimal,
    tanggal_berlaku=None,
    user: User | None = None,
    auto_pengumuman: bool = True,
) -> RiwayatHarga:
    """Record a scheduled price change.

    Args:
        kategori: KategoriSampah instance
        harga_lama: Current price (before change)
        harga_baru: New price to apply
        tanggal_berlaku: When the new price takes effect (min H+3 from now)
        user: User making the change
        auto_pengumuman: Whether to auto-create an announcement

    Returns:
        The created RiwayatHarga instance

    Raises:
        ValueError: If tanggal_berlaku < H+3 from now
    """
    if harga_lama == harga_baru:
        raise ValueError('Harga baru harus berbeda dari harga lama.')

    # Gunakan satu referensi waktu untuk menghindari race condition
    now = timezone.now()

    if tanggal_berlaku is None:
        tanggal_berlaku = now + timedelta(hours=H3_MINIMUM_HOURS)

    validate_tanggal_berlaku(tanggal_berlaku, ref_time=now)

    if user is None:
        user = get_current_user()

    entry = RiwayatHarga.objects.create(
        kategori=kategori,
        harga_lama=harga_lama,
        harga_baru=harga_baru,
        tanggal_berlaku=tanggal_berlaku,
        diubah_oleh=user if user and user.is_authenticated else None,
    )

    if auto_pengumuman:
        _auto_create_pengumuman(kategori, harga_lama, harga_baru, tanggal_berlaku)

    return entry


def get_price_history(kategori_id: int):
    """Return price history queryset for a category."""
    return (
        RiwayatHarga.objects.filter(kategori_id=kategori_id)
        .select_related('diubah_oleh', 'kategori')
        .order_by('-tanggal_berlaku')
    )


def get_active_price(kategori: KategoriSampah) -> tuple[Decimal, str]:
    """Get the currently active price for a category.

    Checks if there's a scheduled price change that has become effective.
    If so, updates the category's harga_beli_per_kg and returns the new price.

    Returns:
        Tuple of (active_price, source_description)
    """
    now = timezone.now()
    pending = (
        RiwayatHarga.objects
        .filter(kategori=kategori, tanggal_berlaku__lte=now)
        .exclude(harga_baru=kategori.harga_beli_per_kg)
        .order_by('-tanggal_berlaku')
        .first()
    )

    if pending:
        kategori.harga_beli_per_kg = pending.harga_baru
        kategori.save(update_fields=['harga_beli_per_kg'])
        return pending.harga_baru, 'auto-applied'

    return kategori.harga_beli_per_kg, 'current'
