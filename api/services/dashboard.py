"""Aggregated data for the monitoring dashboard (Modul 15)."""

from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from api.models import (
    DetailSetoran,
    PenarikanSaldo,
    Penjemputan,
    PenukaranPoin,
    Pengaduan,
    TransaksiSetoran,
    User,
    WilayahLayanan,
)

from .aggregates import fmt, stok_per_kategori
from .periods import day_bounds, month_bounds, parse_int, project_tz, range_bounds
from .pickups import PETUGAS_VISIBLE_STATUSES

ACTIVE_WINDOW_DAYS = 30


def get_overview() -> dict:
    now = timezone.now()
    since = now - timedelta(days=ACTIVE_WINDOW_DAYS)

    total_nasabah = User.objects.filter(role='nasabah').count()
    nasabah_aktif = (
        TransaksiSetoran.objects
        .filter(tanggal__gte=since)
        .values('nasabah_id')
        .distinct()
        .count()
    )
    total_sampah = DetailSetoran.objects.aggregate(total=Sum('berat_kg'))['total']
    total_nilai = TransaksiSetoran.objects.aggregate(total=Sum('total_nilai'))['total']
    total_penarikan = (
        PenarikanSaldo.objects
        .filter(status='selesai')
        .aggregate(total=Sum('nominal'))['total']
    )

    return {
        'total_nasabah': total_nasabah,
        'nasabah_aktif_30_hari': nasabah_aktif,
        'total_sampah_kg': fmt(total_sampah),
        'total_nilai_setoran': fmt(total_nilai),
        'total_penarikan': fmt(total_penarikan),
        'total_penukaran_poin': PenukaranPoin.objects.filter(status='selesai').count(),
        'penjemputan_menunggu': Penjemputan.objects.filter(status='menunggu').count(),
        'pengaduan_terbuka': Pengaduan.objects.filter(status='terbuka').count(),
        'stok_per_kategori': stok_per_kategori(),
        'wilayah_teraktif': _wilayah_teraktif(),
    }


def get_petugas_overview(user: User) -> dict:
    """Ringkasan widget untuk role petugas (bukan angka admin penuh)."""
    start_dt, end_dt = day_bounds(timezone.localdate())

    jemput_hari_ini = Penjemputan.objects.filter(
        petugas=user,
        jadwal__range=(start_dt, end_dt),
        status__in=PETUGAS_VISIBLE_STATUSES,
    ).count()

    antrian_aktif = Penjemputan.objects.filter(
        petugas=user,
        status__in=PETUGAS_VISIBLE_STATUSES,
    ).count()

    return {
        'role': 'petugas',
        'jemput_ditugaskan_hari_ini': jemput_hari_ini,
        'antrian_aktif': antrian_aktif,
    }


def _wilayah_teraktif() -> list[dict]:
    """Daftar kelurahan dengan jumlah nasabah aktif terbanyak."""
    rows = (
        User.objects
        .filter(role='nasabah', is_active=True, kelurahan__isnull=False)
        .values('kelurahan_id', 'kelurahan__kelurahan')
        .annotate(jumlah=Count('id'))
        .order_by('-jumlah')[:5]
    )
    if not rows.exists():
        return []
    return [
        {'kelurahan': row['kelurahan__kelurahan'], 'jumlah_nasabah': row['jumlah']}
        for row in rows
    ]


def get_deposit_chart(bulan, tahun) -> dict:
    now = timezone.localtime(timezone.now())
    month = parse_int(bulan, 'bulan', minimum=1, maximum=12) if bulan else now.month
    year = parse_int(tahun, 'tahun', minimum=2000, maximum=2100) if tahun else now.year

    first_day, last_day = month_bounds(month, year)
    start_dt, end_dt = range_bounds(first_day, last_day)
    tz = project_tz()

    rows = (
        TransaksiSetoran.objects
        .filter(tanggal__range=(start_dt, end_dt))
        .annotate(hari=TruncDate('tanggal', tzinfo=tz))
        .values('hari')
        .annotate(total_nilai=Sum('total_nilai'), jumlah_transaksi=Count('id'))
        .order_by('hari')
    )
    by_day = {
        row['hari']: {
            'total_nilai': fmt(row['total_nilai']),
            'jumlah_transaksi': row['jumlah_transaksi'],
        }
        for row in rows
    }

    berat_rows = (
        DetailSetoran.objects
        .filter(transaksi__tanggal__range=(start_dt, end_dt))
        .annotate(hari=TruncDate('transaksi__tanggal', tzinfo=tz))
        .values('hari')
        .annotate(total_berat=Sum('berat_kg'))
    )
    berat_by_day = {row['hari']: row['total_berat'] for row in berat_rows}

    data = []
    current = first_day
    while current <= last_day:
        day_data = by_day.get(current, {'total_nilai': '0.00', 'jumlah_transaksi': 0})
        data.append({
            'tanggal': current.isoformat(),
            'total_nilai': day_data['total_nilai'],
            'total_berat_kg': fmt(berat_by_day.get(current)),
            'jumlah_transaksi': day_data['jumlah_transaksi'],
        })
        current += timedelta(days=1)

    return {'bulan': month, 'tahun': year, 'data': data}


def _recent_setoran(limit: int) -> list[dict]:
    return [
        {
            '_sort': row.tanggal,
            'type': 'setoran',
            'id': row.id,
            'tanggal': row.tanggal.isoformat(),
            'nasabah': row.nasabah.nama_lengkap if row.nasabah else None,
            'nominal': fmt(row.total_nilai),
            'status': row.status,
        }
        for row in TransaksiSetoran.objects.select_related('nasabah').order_by('-tanggal')[:limit]
    ]


def _recent_penarikan(limit: int) -> list[dict]:
    return [
        {
            '_sort': row.tanggal,
            'type': 'penarikan',
            'id': row.id,
            'tanggal': row.tanggal.isoformat(),
            'nasabah': row.nasabah.nama_lengkap if row.nasabah else None,
            'nominal': fmt(row.nominal),
            'status': row.status,
        }
        for row in PenarikanSaldo.objects.select_related('nasabah').order_by('-tanggal')[:limit]
    ]


def _recent_penjemputan(limit: int) -> list[dict]:
    return [
        {
            '_sort': row.jadwal,
            'type': 'penjemputan',
            'id': row.id,
            'tanggal': row.jadwal.isoformat(),
            'nasabah': row.nasabah.nama_lengkap if row.nasabah else None,
            'estimasi_berat_kg': fmt(row.estimasi_berat),
            'status': row.status,
        }
        for row in Penjemputan.objects.select_related('nasabah').order_by('-jadwal')[:limit]
    ]


def get_recent_activity(limit) -> list[dict]:
    limit = parse_int(limit, 'limit', minimum=1, maximum=50) if limit else 10

    items = (
        _recent_setoran(limit)
        + _recent_penarikan(limit)
        + _recent_penjemputan(limit)
    )
    items.sort(key=lambda row: row['_sort'], reverse=True)
    items = items[:limit]
    for row in items:
        row.pop('_sort')
    return items
