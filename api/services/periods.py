"""Helpers for parsing dates and building timezone-aware period ranges.

All report/dashboard aggregation filters run against ``DateTimeField`` columns,
so callers convert local calendar dates into aware ``datetime`` bounds using the
project timezone (``Asia/Jayapura``) to keep results consistent regardless of
the database backend.
"""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from rest_framework.exceptions import ValidationError


def project_tz() -> ZoneInfo:
    return ZoneInfo(settings.TIME_ZONE)


def parse_date(value: str | None, field: str = 'tanggal') -> date:
    if not value:
        raise ValidationError({field: ['Parameter tanggal wajib diisi (format: YYYY-MM-DD).']})
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            {field: ['Format tanggal tidak valid. Gunakan YYYY-MM-DD.']}
        ) from exc


def parse_int(value, field: str, *, minimum: int | None = None, maximum: int | None = None) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field: ['Nilai harus berupa angka.']}) from exc
    if minimum is not None and parsed < minimum:
        raise ValidationError({field: [f'Nilai minimal {minimum}.']})
    if maximum is not None and parsed > maximum:
        raise ValidationError({field: [f'Nilai maksimal {maximum}.']})
    return parsed


def day_bounds(day: date) -> tuple[datetime, datetime]:
    tz = project_tz()
    start = datetime.combine(day, time.min, tzinfo=tz)
    end = datetime.combine(day, time.max, tzinfo=tz)
    return start, end


def range_bounds(start_day: date, end_day: date) -> tuple[datetime, datetime]:
    if start_day > end_day:
        raise ValidationError({'periode': ['Tanggal mulai tidak boleh setelah tanggal akhir.']})
    tz = project_tz()
    start = datetime.combine(start_day, time.min, tzinfo=tz)
    end = datetime.combine(end_day, time.max, tzinfo=tz)
    return start, end


def iso_week_bounds(week: int, year: int) -> tuple[date, date]:
    """Return the Monday..Sunday date range for an ISO week number."""
    if not 1 <= week <= 53:
        raise ValidationError({'minggu': ['Nomor minggu harus antara 1 dan 53.']})
    try:
        monday = date.fromisocalendar(year, week, 1)
    except ValueError as exc:
        raise ValidationError(
            {'minggu': [f'Minggu {week} tidak valid untuk tahun {year}.']}
        ) from exc
    return monday, monday + timedelta(days=6)


def month_bounds(month: int, year: int) -> tuple[date, date]:
    if not 1 <= month <= 12:
        raise ValidationError({'bulan': ['Bulan harus antara 1 dan 12.']})
    first = date(year, month, 1)
    if month == 12:
        last = date(year, 12, 31)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    return first, last
