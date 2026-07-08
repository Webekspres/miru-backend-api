"""Business rules and orchestration for partner waste sales."""

from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from api.models import KategoriSampah, MitraPengepul, PenjualanMitra
from api.services.ledger import InsufficientStokError, decrease_kategori_stok


def validate_berat_jual(berat_jual_kg: Decimal) -> Decimal:
    if berat_jual_kg <= 0:
        raise ValidationError('Berat jual harus lebih dari 0 kg.')
    return berat_jual_kg


def validate_harga_jual(harga_jual_per_kg: Decimal) -> Decimal:
    if harga_jual_per_kg <= 0:
        raise ValidationError('Harga jual harus lebih dari 0.')
    return harga_jual_per_kg


def validate_stok_cukup(kategori: KategoriSampah, berat_jual_kg: Decimal) -> None:
    kategori.refresh_from_db()
    if kategori.stok_terkini_kg < berat_jual_kg:
        raise InsufficientStokError(
            f'Stok tidak mencukupi. Tersedia: {kategori.stok_terkini_kg} kg, '
            f'diminta: {berat_jual_kg} kg.'
        )


def build_sale_data(
    mitra: MitraPengepul,
    kategori: KategoriSampah,
    berat_jual_kg: Decimal,
    harga_jual_per_kg: Decimal,
) -> dict:
    validate_berat_jual(berat_jual_kg)
    validate_harga_jual(harga_jual_per_kg)
    validate_stok_cukup(kategori, berat_jual_kg)

    return {
        'mitra': mitra,
        'kategori': kategori,
        'berat_jual_kg': berat_jual_kg,
        'harga_jual_per_kg': harga_jual_per_kg,
        'total_penjualan': berat_jual_kg * harga_jual_per_kg,
    }


@transaction.atomic
def create_partner_sale_with_side_effects(sale_data: dict) -> PenjualanMitra:
    """Create partner sale record and decrease category stock atomically."""
    prepared = build_sale_data(
        sale_data['mitra'],
        sale_data['kategori'],
        sale_data['berat_jual_kg'],
        sale_data['harga_jual_per_kg'],
    )
    instance = PenjualanMitra.objects.create(**prepared)
    decrease_kategori_stok(instance.kategori, instance.berat_jual_kg)
    return instance
