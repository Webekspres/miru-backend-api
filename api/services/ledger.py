"""Atomic ledger operations for saldo, poin, and stok with row-level locking."""

from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from api.models import DetailSetoran, KategoriSampah, Reward, TransaksiSetoran, User


class InsufficientSaldoError(ValidationError):
    default_detail = 'Saldo tidak mencukupi.'
    default_code = 'insufficient_saldo'


class InsufficientPoinError(ValidationError):
    default_detail = 'Poin tidak mencukupi.'
    default_code = 'insufficient_poin'


class InsufficientStokError(ValidationError):
    default_detail = 'Stok tidak mencukupi.'
    default_code = 'insufficient_stok'


def _lock_user(user_id: int) -> User:
    return User.objects.select_for_update().get(pk=user_id)


def _lock_kategori(kategori_id: int) -> KategoriSampah:
    return KategoriSampah.objects.select_for_update().get(pk=kategori_id)


def _ensure_non_negative_saldo(saldo: Decimal) -> None:
    if saldo < 0:
        raise InsufficientSaldoError('Saldo tidak boleh negatif.')


def _ensure_non_negative_poin(poin: int) -> None:
    if poin < 0:
        raise InsufficientPoinError('Poin tidak boleh negatif.')


def _ensure_non_negative_stok(stok: Decimal) -> None:
    if stok < 0:
        raise InsufficientStokError('Stok tidak boleh negatif.')


def _lock_reward(reward_id: int) -> Reward:
    return Reward.objects.select_for_update().get(pk=reward_id)


def _ensure_non_negative_reward_stok(stok: int) -> None:
    if stok < 0:
        raise InsufficientStokError('Stok reward tidak boleh negatif.')


@transaction.atomic
def decrease_reward_stok(reward: Reward, jumlah: int = 1) -> Reward:
    """Decrease reward stock; raises if result would be negative."""
    locked = _lock_reward(reward.pk)
    if locked.stok < jumlah:
        raise InsufficientStokError(
            f'Stok reward tidak mencukupi. Tersedia: {locked.stok}, dibutuhkan: {jumlah}.'
        )
    locked.stok -= jumlah
    _ensure_non_negative_reward_stok(locked.stok)
    locked.save(update_fields=['stok'])
    return locked


@transaction.atomic
def complete_penukaran_poin(
    nasabah: User,
    reward: Reward,
    *,
    poin: int | None = None,
    qty: int = 1,
) -> tuple[User, Reward]:
    """Atomically debit poin and decrease reward stock on redemption approval.

    `poin` should be the snapshot from PenukaranPoin.poin_dibutuhkan when available;
    falls back to current reward catalog price only for legacy callers.
    """
    poin_to_debit = reward.poin_dibutuhkan if poin is None else poin
    user = debit_nasabah_poin(nasabah, poin_to_debit)
    reward_locked = decrease_reward_stok(reward, qty)
    return user, reward_locked


@transaction.atomic
def credit_nasabah_setoran(
    nasabah: User, total_nilai: Decimal,
    setoran: TransaksiSetoran | None = None,
) -> User:
    """Credit saldo and poin from a deposit; locks nasabah row.

    If `setoran` is provided, also creates a PoinTransaksi record
    to track 1-year expiry (Fase 8.5).
    """
    locked = _lock_user(nasabah.pk)
    poin_didapat = int(total_nilai / 1000)
    locked.saldo += total_nilai
    locked.poin += poin_didapat
    _ensure_non_negative_saldo(locked.saldo)
    _ensure_non_negative_poin(locked.poin)
    locked.save(update_fields=['saldo', 'poin'])

    # Track poin for 1-year expiry tracking
    if poin_didapat > 0 and setoran is not None:
        from datetime import timedelta
        from django.utils import timezone
        from api.models import PoinTransaksi
        PoinTransaksi.objects.create(
            user=nasabah,
            sumber='setoran',
            setoran=setoran,
            jumlah=poin_didapat,
            sisa=poin_didapat,
            tanggal_kedaluwarsa=timezone.now() + timedelta(days=365),
        )

    return locked


@transaction.atomic
def adjust_setoran_correction(
    nasabah: User, old_total: Decimal, new_total: Decimal,
) -> User:
    """Adjust nasabah saldo/poin when admin corrects a deposit total."""
    delta_saldo = new_total - old_total
    delta_poin = int(new_total / 1000) - int(old_total / 1000)
    if delta_saldo == 0 and delta_poin == 0:
        return nasabah

    locked = _lock_user(nasabah.pk)
    locked.saldo += delta_saldo
    locked.poin += delta_poin
    _ensure_non_negative_saldo(locked.saldo)
    _ensure_non_negative_poin(locked.poin)
    locked.save(update_fields=['saldo', 'poin'])
    return locked


@transaction.atomic
def debit_nasabah_saldo(nasabah: User, nominal: Decimal) -> User:
    """Debit nasabah saldo; raises if result would be negative."""
    locked = _lock_user(nasabah.pk)
    if locked.saldo < nominal:
        raise InsufficientSaldoError(
            f'Saldo tidak mencukupi. Tersedia: Rp{locked.saldo}, diminta: Rp{nominal}.'
        )
    locked.saldo -= nominal
    _ensure_non_negative_saldo(locked.saldo)
    locked.save(update_fields=['saldo'])
    return locked


@transaction.atomic
def debit_nasabah_poin(nasabah: User, poin: int) -> User:
    """Debit nasabah poin; raises if result would be negative."""
    locked = _lock_user(nasabah.pk)
    if locked.poin < poin:
        raise InsufficientPoinError(
            f'Poin tidak mencukupi. Tersedia: {locked.poin}, dibutuhkan: {poin}.'
        )
    locked.poin -= poin
    _ensure_non_negative_poin(locked.poin)
    locked.save(update_fields=['poin'])
    return locked


@transaction.atomic
def increase_kategori_stok(kategori: KategoriSampah, berat_kg: Decimal) -> KategoriSampah:
    """Increase waste category stock; locks kategori row."""
    locked = _lock_kategori(kategori.pk)
    locked.stok_terkini_kg += berat_kg
    _ensure_non_negative_stok(locked.stok_terkini_kg)
    locked.save(update_fields=['stok_terkini_kg'])
    return locked


@transaction.atomic
def decrease_kategori_stok(kategori: KategoriSampah, berat_kg: Decimal) -> KategoriSampah:
    """Decrease waste category stock; raises if result would be negative."""
    locked = _lock_kategori(kategori.pk)
    if locked.stok_terkini_kg < berat_kg:
        raise InsufficientStokError(
            f'Stok tidak mencukupi. Tersedia: {locked.stok_terkini_kg} kg, '
            f'diminta: {berat_kg} kg.'
        )
    locked.stok_terkini_kg -= berat_kg
    _ensure_non_negative_stok(locked.stok_terkini_kg)
    locked.save(update_fields=['stok_terkini_kg'])
    return locked


@transaction.atomic
def create_setoran_with_side_effects(
    transaksi_data: dict,
    details_data: list[dict],
) -> TransaksiSetoran:
    """Create deposit transaction and apply all side effects atomically."""
    transaksi = TransaksiSetoran.objects.create(**transaksi_data)

    total_nilai = Decimal('0')
    for detail in details_data:
        detail_obj = DetailSetoran.objects.create(transaksi=transaksi, **detail)
        total_nilai += detail_obj.subtotal
        increase_kategori_stok(detail['kategori'], detail['berat_kg'])

    transaksi.total_nilai = total_nilai
    transaksi.save(update_fields=['total_nilai'])

    credit_nasabah_setoran(transaksi.nasabah, total_nilai, setoran=transaksi)

    # Notifikasi SETELAH total_nilai di-set (bukan saat create dengan default 0).
    if transaksi.nasabah_id and total_nilai > 0:
        from api.services.notifications import create_notification

        nilai_fmt = f'{total_nilai:,.0f}'.replace(',', '.')
        create_notification(
            user_id=transaksi.nasabah_id,
            judul='Setoran Sampah Berhasil',
            deskripsi=(
                f'Setoran sampah sebesar Rp{nilai_fmt} '
                f'telah dicatat ke akun Anda. Cek saldo di halaman utama.'
            ),
            kategori='setoran',
        )

    return transaksi
