"""Atomic ledger operations for saldo, poin, and stok with row-level locking."""

from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from api.models import DetailSetoran, KategoriSampah, TransaksiSetoran, User


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


@transaction.atomic
def credit_nasabah_setoran(nasabah: User, total_nilai: Decimal) -> User:
    """Credit saldo and poin from a deposit; locks nasabah row."""
    locked = _lock_user(nasabah.pk)
    locked.saldo += total_nilai
    locked.poin += int(total_nilai / 1000)
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

    credit_nasabah_setoran(transaksi.nasabah, total_nilai)
    return transaksi
