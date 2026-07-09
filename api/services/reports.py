"""Report aggregations (Modul 16) — harian, mingguan, bulanan, sampah, evaluasi."""

from django.db.models import Sum
from django.utils import timezone

from api.models import PenukaranPoin, TransaksiSetoran, User

from .aggregates import (
    fmt,
    penarikan_total,
    penukaran_count,
    setoran_summary,
    tonase_per_jenis,
)
from .periods import (
    day_bounds,
    iso_week_bounds,
    month_bounds,
    parse_date,
    parse_int,
    range_bounds,
)


def daily_report(tanggal) -> dict:
    day = parse_date(tanggal)
    start_dt, end_dt = day_bounds(day)
    summary = setoran_summary(start_dt, end_dt)
    return {
        'tanggal': day.isoformat(),
        'jumlah_transaksi': summary['jumlah_transaksi'],
        'total_setoran': summary['total_nilai_setoran'],
        'total_penarikan': penarikan_total(start_dt, end_dt),
        'total_sampah_kg': summary['total_sampah_kg'],
        'tonase_per_jenis': tonase_per_jenis(start_dt, end_dt),
    }


def _nasabah_baru(start_dt, end_dt) -> int:
    return User.objects.filter(
        role='nasabah', date_joined__range=(start_dt, end_dt),
    ).count()


def weekly_report(minggu, tahun) -> dict:
    now = timezone.localtime(timezone.now())
    iso_year, iso_week, _ = now.isocalendar()
    week = parse_int(minggu, 'minggu', minimum=1, maximum=53) if minggu else iso_week
    year = parse_int(tahun, 'tahun', minimum=2000, maximum=2100) if tahun else iso_year

    start_day, end_day = iso_week_bounds(week, year)
    start_dt, end_dt = range_bounds(start_day, end_day)
    summary = setoran_summary(start_dt, end_dt)

    return {
        'minggu': week,
        'tahun': year,
        'periode': {'mulai': start_day.isoformat(), 'selesai': end_day.isoformat()},
        'jumlah_transaksi': summary['jumlah_transaksi'],
        'total_setoran': summary['total_nilai_setoran'],
        'total_penarikan': penarikan_total(start_dt, end_dt),
        'total_sampah_kg': summary['total_sampah_kg'],
        'nasabah_baru': _nasabah_baru(start_dt, end_dt),
        'tonase_per_jenis': tonase_per_jenis(start_dt, end_dt),
    }


def monthly_report(bulan, tahun) -> dict:
    now = timezone.localtime(timezone.now())
    month = parse_int(bulan, 'bulan', minimum=1, maximum=12) if bulan else now.month
    year = parse_int(tahun, 'tahun', minimum=2000, maximum=2100) if tahun else now.year

    first_day, last_day = month_bounds(month, year)
    start_dt, end_dt = range_bounds(first_day, last_day)
    summary = setoran_summary(start_dt, end_dt)

    total_saldo_beredar = User.objects.filter(role='nasabah').aggregate(
        total=Sum('saldo'),
    )['total']
    nasabah_aktif = (
        TransaksiSetoran.objects
        .filter(tanggal__range=(start_dt, end_dt))
        .values('nasabah_id')
        .distinct()
        .count()
    )

    return {
        'bulan': month,
        'tahun': year,
        'periode': {'mulai': first_day.isoformat(), 'selesai': last_day.isoformat()},
        'jumlah_nasabah_terdaftar': User.objects.filter(role='nasabah').count(),
        'jumlah_nasabah_aktif': nasabah_aktif,
        'jumlah_transaksi': summary['jumlah_transaksi'],
        'total_sampah_kg': summary['total_sampah_kg'],
        'total_nilai_setoran': summary['total_nilai_setoran'],
        'total_penarikan': penarikan_total(start_dt, end_dt),
        'total_saldo_beredar': fmt(total_saldo_beredar),
        'jumlah_reward_ditukar': penukaran_count(start_dt, end_dt),
        'tonase_per_jenis': tonase_per_jenis(start_dt, end_dt),
    }


def waste_report(start, end) -> dict:
    start_day = parse_date(start, 'start')
    end_day = parse_date(end, 'end')
    start_dt, end_dt = range_bounds(start_day, end_day)
    per_jenis = tonase_per_jenis(start_dt, end_dt)

    total_berat = sum(float(row['total_berat_kg']) for row in per_jenis)
    total_nilai = sum(float(row['total_nilai']) for row in per_jenis)

    return {
        'periode': {'mulai': start_day.isoformat(), 'selesai': end_day.isoformat()},
        'total_berat_kg': f'{total_berat:.2f}',
        'total_nilai': f'{total_nilai:.2f}',
        'per_kategori': per_jenis,
    }


def evaluation_report(start, end) -> dict:
    start_day = parse_date(start, 'start')
    end_day = parse_date(end, 'end')
    start_dt, end_dt = range_bounds(start_day, end_day)
    summary = setoran_summary(start_dt, end_dt)

    nasabah_aktif = (
        TransaksiSetoran.objects
        .filter(tanggal__range=(start_dt, end_dt))
        .values('nasabah_id')
        .distinct()
        .count()
    )
    reward_ditukar = penukaran_count(start_dt, end_dt)
    poin_ditukar = (
        PenukaranPoin.objects
        .filter(tanggal__range=(start_dt, end_dt), status='selesai')
        .aggregate(total=Sum('reward__poin_dibutuhkan'))['total']
    )

    return {
        'periode': {'mulai': start_day.isoformat(), 'selesai': end_day.isoformat()},
        'jumlah_nasabah_terdaftar': User.objects.filter(role='nasabah').count(),
        'jumlah_nasabah_aktif': nasabah_aktif,
        'nasabah_baru': _nasabah_baru(start_dt, end_dt),
        'jumlah_transaksi': summary['jumlah_transaksi'],
        'total_sampah_kg': summary['total_sampah_kg'],
        'total_nilai_setoran': summary['total_nilai_setoran'],
        'total_penarikan': penarikan_total(start_dt, end_dt),
        'jumlah_reward_ditukar': reward_ditukar,
        'total_poin_ditukar': poin_ditukar or 0,
        'tonase_per_jenis': tonase_per_jenis(start_dt, end_dt),
    }
