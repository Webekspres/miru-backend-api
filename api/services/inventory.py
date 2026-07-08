"""Warehouse stock summary and history (Modul 12)."""

from decimal import Decimal

from django.shortcuts import get_object_or_404

from api.models import DetailSetoran, KategoriSampah, PenjualanMitra

from .aggregates import fmt
from .periods import parse_int


def get_inventory_summary() -> dict:
    kategori_list = []
    total_berat = Decimal('0')
    total_nilai = Decimal('0')

    for kat in KategoriSampah.objects.all().order_by('nama'):
        stok = kat.stok_terkini_kg or Decimal('0')
        estimasi_nilai = stok * (kat.harga_beli_per_kg or Decimal('0'))
        total_berat += stok
        total_nilai += estimasi_nilai
        kategori_list.append({
            'kategori_id': kat.id,
            'nama': kat.nama,
            'harga_beli_per_kg': fmt(kat.harga_beli_per_kg),
            'stok_terkini_kg': fmt(stok),
            'estimasi_nilai': fmt(estimasi_nilai),
        })

    return {
        'total_stok_kg': fmt(total_berat),
        'total_estimasi_nilai': fmt(total_nilai),
        'kategori': kategori_list,
    }


def _setoran_history(kategori_id: int) -> list[dict]:
    return [
        {
            '_sort': row.transaksi.tanggal,
            'id': row.id,
            'tanggal': row.transaksi.tanggal.isoformat(),
            'arah': 'masuk',
            'berat_kg': fmt(row.berat_kg),
            'sumber': 'setoran',
            'referensi_id': row.transaksi_id,
        }
        for row in (
            DetailSetoran.objects
            .filter(kategori_id=kategori_id)
            .select_related('transaksi')
            .order_by('-transaksi__tanggal')
        )
    ]


def _penjualan_history(kategori_id: int) -> list[dict]:
    return [
        {
            '_sort': row.tanggal,
            'id': row.id,
            'tanggal': row.tanggal.isoformat(),
            'arah': 'keluar',
            'berat_kg': fmt(row.berat_jual_kg),
            'sumber': 'penjualan_mitra',
            'referensi_id': row.id,
        }
        for row in PenjualanMitra.objects.filter(kategori_id=kategori_id).order_by('-tanggal')
    ]


def get_inventory_history(kategori_id: int, limit=None) -> dict:
    """Riwayat perubahan stok dari setoran (masuk) dan penjualan mitra (keluar)."""
    kategori = get_object_or_404(KategoriSampah, pk=kategori_id)
    limit = parse_int(limit, 'limit', minimum=1, maximum=100) if limit else 50

    items = _setoran_history(kategori_id) + _penjualan_history(kategori_id)
    items.sort(key=lambda row: row['_sort'], reverse=True)
    items = items[:limit]
    for row in items:
        row.pop('_sort')

    return {
        'kategori_id': kategori.id,
        'nama': kategori.nama,
        'stok_terkini_kg': fmt(kategori.stok_terkini_kg),
        'history': items,
    }
