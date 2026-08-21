"""Shared aggregation helpers for dashboard and report endpoints."""

from decimal import Decimal

from django.db.models import Count, Sum

from api.models import (
    DetailSetoran,
    KategoriSampah,
    PenarikanSaldo,
    PenukaranPoin,
    TransaksiSetoran,
)

ZERO = Decimal('0.00')


def fmt(value) -> str:
    """Format a Decimal/number as a fixed 2-decimal string ('0.00' for None)."""
    if value is None:
        return '0.00'
    return f'{Decimal(value):.2f}'


def tonase_per_jenis(start_dt, end_dt) -> list[dict]:
    """Total berat (kg) and nilai (Rp) grouped per kategori for a period."""
    rows = (
        DetailSetoran.objects
        .filter(transaksi__tanggal__range=(start_dt, end_dt))
        .values('kategori_id', 'kategori__nama')
        .annotate(total_berat_kg=Sum('berat_kg'), total_nilai=Sum('subtotal'))
        .order_by('kategori__nama')
    )
    return [
        {
            'kategori_id': row['kategori_id'],
            'nama': row['kategori__nama'],
            'total_berat_kg': fmt(row['total_berat_kg']),
            'total_nilai': fmt(row['total_nilai']),
        }
        for row in rows
    ]


def setoran_summary(start_dt, end_dt) -> dict:
    setoran = TransaksiSetoran.objects.filter(tanggal__range=(start_dt, end_dt))
    berat = (
        DetailSetoran.objects
        .filter(transaksi__tanggal__range=(start_dt, end_dt))
        .aggregate(total=Sum('berat_kg'))
    )
    agg = setoran.aggregate(total=Sum('total_nilai'), jumlah=Count('id'))
    return {
        'jumlah_transaksi': agg['jumlah'] or 0,
        'total_nilai_setoran': fmt(agg['total']),
        'total_sampah_kg': fmt(berat['total']),
    }


def penarikan_total(start_dt, end_dt, *, status: str = 'selesai') -> str:
    agg = (
        PenarikanSaldo.objects
        .filter(tanggal__range=(start_dt, end_dt), status=status)
        .aggregate(total=Sum('nominal'))
    )
    return fmt(agg['total'])


def penukaran_count(start_dt, end_dt, *, status: str = 'selesai') -> int:
    return PenukaranPoin.objects.filter(
        tanggal__range=(start_dt, end_dt), status=status,
    ).count()


def stok_per_kategori() -> list[dict]:
    return [
        {
            'kategori_id': kat.id,
            'nama': kat.nama,
            'harga_beli_per_kg': fmt(kat.harga_beli_per_kg),
            'stok_terkini_kg': fmt(kat.stok_terkini_kg),
        }
        for kat in KategoriSampah.objects.all().order_by('nama')
    ]
