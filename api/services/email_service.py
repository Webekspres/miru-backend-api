"""
Transactional email service for MIRU admin notifications (Fase 8.6).

Mengirim email ke admin untuk event operasional:
- Penjemputan baru diajukan
- Ringkasan harian (opsional, via scheduled task)

Semua kredensial SMTP dari environment (settings.py).
Payload TIDAK mengandung NIK, KTP, atau token (sesuai security §11).
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger('miru.request')


def send_admin_email(
    subject: str,
    message: str,
    html_message: str | None = None,
) -> bool:
    """
    Kirim email ke admin.

    Args:
        subject: Judul email.
        message: Teks plaintext.
        html_message: Opsional, versi HTML.

    Returns:
        True jika berhasil, False jika gagal atau tidak ada tujuan.
    """
    to = getattr(settings, 'ADMIN_NOTIF_EMAIL', '')
    if not to:
        logger.warning('ADMIN_NOTIF_EMAIL tidak dikonfigurasi — email tidak dikirim.')
        return False

    try:
        send_mail(
            subject=f'[MIRU] {subject}',
            message=message,
            html_message=html_message,
            from_email=None,  # pakai DEFAULT_FROM_EMAIL
            recipient_list=[to],
            fail_silently=False,
        )
        logger.info('Email admin terkirim: %s -> %s', subject, to)
        return True
    except Exception as exc:
        logger.error('Gagal kirim email admin: %s — %s', subject, exc)
        return False


def notify_admin_new_pickup(pickup) -> None:
    """Kirim notifikasi email ke admin saat ada penjemputan baru."""
    nasabah = pickup.nasabah
    subject = 'Penjemputan Baru Diajukan'
    message = (
        f'Penjemputan sampah baru telah diajukan:\n\n'
        f'Nasabah: {nasabah.nama_lengkap} (No. HP: {nasabah.no_hp})\n'
        f'Alamat: {pickup.alamat_jemput}\n'
        f'Estimasi Berat: {pickup.estimasi_berat} kg\n'
        f'Jadwal: {timezone.localtime(pickup.jadwal).strftime("%d %b %Y %H:%M")} WIT\n'
        f'Status: {pickup.get_status_display()}\n\n'
        f'Segera tindak lanjuti di panel admin MIRU.\n'
        f'---\n'
        f'MIRU Bank Sampah — Distrik Mimika Baru'
    )
    html_message = (
        f'<h2>Penjemputan Baru Diajukan</h2>'
        f'<table>'
        f'<tr><td><b>Nasabah</b></td><td>{nasabah.nama_lengkap}</td></tr>'
        f'<tr><td><b>No. HP</b></td><td>{nasabah.no_hp}</td></tr>'
        f'<tr><td><b>Alamat</b></td><td>{pickup.alamat_jemput}</td></tr>'
        f'<tr><td><b>Estimasi Berat</b></td><td>{pickup.estimasi_berat} kg</td></tr>'
        f'<tr><td><b>Jadwal</b></td><td>'
        f'{timezone.localtime(pickup.jadwal).strftime("%d %b %Y %H:%M")} WIT'
        f'</td></tr>'
        f'<tr><td><b>Status</b></td><td>{pickup.get_status_display()}</td></tr>'
        f'</table>'
        f'<p>Segera tindak lanjuti di panel admin MIRU.</p>'
        f'<hr><p><small>MIRU Bank Sampah — Distrik Mimika Baru</small></p>'
    )
    send_admin_email(subject, message, html_message)


def send_daily_summary() -> None:
    """
    Kirim ringkasan harian ke admin.

    Data agregat: jumlah transaksi, total setoran, penjemputan menunggu, dll.
    """
    from django.db.models import Count, Sum
    from api.models import Penjemputan, TransaksiSetoran

    today = timezone.localtime(timezone.now()).date()
    from api.services.periods import day_bounds
    start_dt, end_dt = day_bounds(today)

    setoran = TransaksiSetoran.objects.filter(tanggal__range=(start_dt, end_dt))
    setoran_agg = setoran.aggregate(
        jumlah=Count('id'), total=Sum('total_nilai'),
    )
    pickup_menunggu = Penjemputan.objects.filter(status='menunggu').count()

    subject = f'Ringkasan Harian — {today.isoformat()}'
    message = (
        f'Ringkasan operasional MIRU Bank Sampah\n'
        f'{today.isoformat()}\n\n'
        f'Transaksi Setoran: {setoran_agg["jumlah"] or 0}\n'
        f'Total Nilai Setoran: Rp{setoran_agg["total"] or 0:,.0f}\n'
        f'Penjemputan Menunggu: {pickup_menunggu}\n\n'
        f'---\n'
        f'MIRU Bank Sampah — Distrik Mimika Baru'
    )
    html_message = (
        f'<h2>Ringkasan Harian</h2>'
        f'<p>{today.isoformat()}</p>'
        f'<table>'
        f'<tr><td><b>Transaksi Setoran</b></td><td>{setoran_agg["jumlah"] or 0}</td></tr>'
        f'<tr><td><b>Total Nilai Setoran</b></td><td>'
        f'Rp{setoran_agg["total"] or 0:,.0f}</td></tr>'
        f'<tr><td><b>Penjemputan Menunggu</b></td><td>{pickup_menunggu}</td></tr>'
        f'</table>'
        f'<hr><p><small>MIRU Bank Sampah — Distrik Mimika Baru</small></p>'
    )
    send_admin_email(subject, message, html_message)
