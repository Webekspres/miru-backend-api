"""Business rules and price calculation for deposit transactions."""

from decimal import Decimal

from rest_framework.exceptions import ValidationError

from api.models import KategoriSampah, User

MIN_BERAT_KG = Decimal('1')
DEPOSIT_STAFF_ROLES = ('petugas', 'admin')


def validate_nasabah_for_setoran(nasabah: User) -> User:
    if nasabah.role != 'nasabah':
        raise ValidationError('User yang dipilih bukan nasabah.')
    if not nasabah.is_active:
        raise ValidationError('Nasabah tidak aktif.')
    return nasabah


def validate_petugas_for_setoran(user: User) -> User:
    if user.role not in DEPOSIT_STAFF_ROLES:
        raise ValidationError('Hanya petugas atau admin yang dapat mencatat setoran.')
    return user


def build_detail_data(kategori: KategoriSampah, berat_kg: Decimal) -> dict:
    harga_saat_itu = kategori.harga_beli_per_kg
    subtotal = berat_kg * harga_saat_itu

    return {
        'kategori': kategori,
        'berat_kg': berat_kg,
        'harga_saat_itu': harga_saat_itu,
        'subtotal': subtotal,
    }


def prepare_details_data(details_input: list[dict]) -> list[dict]:
    if not details_input:
        raise ValidationError({'details': ['Minimal satu detail setoran diperlukan.']})

    return [
        build_detail_data(detail['kategori'], detail['berat_kg'])
        for detail in details_input
    ]
