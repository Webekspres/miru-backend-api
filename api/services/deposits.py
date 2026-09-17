"""Business rules and price calculation for deposit transactions."""

from __future__ import annotations

import json
import re
from decimal import Decimal

from rest_framework.exceptions import ValidationError

from api.models import KategoriSampah, User

MIN_BERAT_KG = Decimal('1')
DEPOSIT_STAFF_ROLES = ('petugas', 'admin')

_ACTIVE_NASABAH = {'role': 'nasabah', 'is_active': True}


def validate_nasabah_for_setoran(nasabah: User) -> User:
    if nasabah.role != 'nasabah':
        raise ValidationError('User yang dipilih bukan nasabah.')
    if not nasabah.is_active:
        raise ValidationError('Nasabah tidak aktif.')
    return nasabah


def _coerce_positive_int(value) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value > 0:
        return value
    if isinstance(value, str) and value.isdigit():
        parsed = int(value)
        if parsed > 0:
            return parsed
    return None


def parse_nasabah_lookup_query(raw: str) -> dict:
    """Parse id angka, username, atau payload QR MIRU JSON {id,...}."""
    trimmed = (raw or '').strip()
    if not trimmed:
        return {}

    if trimmed.isdigit():
        pk = int(trimmed)
        return {'id': pk} if pk > 0 else {}

    try:
        parsed = json.loads(trimmed)
    except (TypeError, ValueError, json.JSONDecodeError):
        parsed = None

    if isinstance(parsed, dict):
        pk = _coerce_positive_int(parsed.get('id'))
        if pk is not None:
            return {'id': pk}

    match = re.search(r"""["']?id["']?\s*[:=]\s*["']?(\d+)""", trimmed, re.I)
    if match:
        pk = int(match.group(1))
        if pk > 0:
            return {'id': pk}

    # Bukan JSON / id — anggap username
    return {'username': trimmed}


def resolve_active_nasabah(raw: str) -> User | None:
    """Cari nasabah aktif by id / username / QR payload. None jika tidak ada."""
    parsed = parse_nasabah_lookup_query(raw)
    if not parsed:
        return None

    qs = User.objects.filter(**_ACTIVE_NASABAH)
    if 'id' in parsed:
        return qs.filter(pk=parsed['id']).first()
    if 'username' in parsed:
        return qs.filter(username__iexact=parsed['username']).first()
    return None


def validate_petugas_for_setoran(user: User) -> User:
    if user.role not in DEPOSIT_STAFF_ROLES:
        raise ValidationError('Hanya petugas atau admin yang dapat mencatat setoran.')
    return user


def build_detail_data(kategori: KategoriSampah, berat_kg: Decimal) -> dict:
    # Auto-apply harga yang sudah efektif jika ada perubahan harga terjadwal
    from api.services.price_history import get_active_price
    harga_saat_itu, _ = get_active_price(kategori)
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


def build_bukti_digital(transaksi) -> dict:
    """Struktur bukti digital untuk nasabah (SOP B.1)."""
    details = []
    for detail in transaksi.details.select_related('kategori').all():
        details.append({
            'id': detail.id,
            'kategori': detail.kategori_id,
            'kategori_nama': detail.kategori.nama,
            'berat_kg': str(detail.berat_kg),
            'harga_saat_itu': str(detail.harga_saat_itu),
            'subtotal': str(detail.subtotal),
        })

    return {
        'id': transaksi.id,
        'tanggal': transaksi.tanggal.isoformat(),
        'total_nilai': f'{transaksi.total_nilai:.2f}',
        'details': details,
    }
