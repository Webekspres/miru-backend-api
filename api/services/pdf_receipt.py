"""
PDF receipt generation for deposit and withdrawal transactions.

Uses reportlab — no system dependencies required.
"""

from __future__ import annotations

import io
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _format_rupiah(value: Decimal) -> str:
    """Format Decimal to Rp currency string."""
    return f'Rp{value:,.0f}'.replace(',', '.')


def generate_deposit_receipt(transaksi) -> bytes:
    """
    Generate PDF bukti setoran untuk TransaksiSetoran.

    Returns PDF as bytes.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A5,
        title=f'Bukti Setoran #{transaksi.id}',
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        leftMargin=10 * mm,
        rightMargin=10 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    heading_style = styles['Heading3']

    elements = []

    # Kop institusi
    elements.append(Paragraph(
        'MIRU Bank Sampah', title_style,
    ))
    elements.append(Paragraph(
        'Distrik Mimika Baru', normal_style,
    ))
    elements.append(Spacer(1, 4 * mm))

    # Judul
    elements.append(Paragraph(
        'BUKTI SETORAN SAMPAH', heading_style,
    ))
    elements.append(Spacer(1, 3 * mm))

    # Info transaksi
    tgl = timezone.localtime(transaksi.tanggal).strftime('%d/%m/%Y %H:%M')
    info_data = [
        ['No. Transaksi', f'#{transaksi.id}'],
        ['Tanggal', tgl],
        ['Nasabah', transaksi.nasabah.nama_lengkap],
        ['Petugas', transaksi.petugas.nama_lengkap if transaksi.petugas else '-'],
    ]
    info_table = Table(info_data, colWidths=[50 * mm, 80 * mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 3 * mm))

    # Detail setoran
    elements.append(Paragraph('Detail Setoran:', heading_style))
    elements.append(Spacer(1, 2 * mm))

    detail_header = [['No', 'Kategori', 'Berat (kg)', 'Harga/kg', 'Subtotal']]
    detail_rows = []
    for i, d in enumerate(transaksi.details.all(), 1):
        detail_rows.append([
            str(i),
            d.kategori.nama,
            f'{d.berat_kg:,.2f}',
            _format_rupiah(d.harga_saat_itu),
            _format_rupiah(d.subtotal),
        ])

    detail_table = Table(
        detail_header + detail_rows,
        colWidths=[10 * mm, 40 * mm, 25 * mm, 25 * mm, 30 * mm],
    )
    detail_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 3 * mm))

    # Total
    total_data = [
        ['Total Nilai', _format_rupiah(transaksi.total_nilai)],
        ['Poin Didapat', str(int(transaksi.total_nilai / 1000))],
    ]
    total_table = Table(total_data, colWidths=[50 * mm, 80 * mm])
    total_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 5 * mm))

    # Footer
    elements.append(Paragraph(
        f'Dicetak: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
        normal_style,
    ))
    elements.append(Paragraph(
        'Terima kasih telah memilah sampah!',
        normal_style,
    ))

    doc.build(elements)
    return buf.getvalue()


def generate_withdrawal_receipt(penarikan) -> bytes:
    """
    Generate PDF tanda terima penarikan saldo.

    Returns PDF as bytes.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A5,
        title=f'Tanda Terima Penarikan #{penarikan.id}',
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        leftMargin=10 * mm,
        rightMargin=10 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    heading_style = styles['Heading3']

    elements = []

    # Kop
    elements.append(Paragraph(
        'MIRU Bank Sampah', title_style,
    ))
    elements.append(Paragraph(
        'Distrik Mimika Baru', normal_style,
    ))
    elements.append(Spacer(1, 4 * mm))

    # Judul
    elements.append(Paragraph(
        'TANDA TERIMA PENARIKAN SALDO', heading_style,
    ))
    elements.append(Spacer(1, 3 * mm))

    # Info
    tgl = timezone.localtime(penarikan.tanggal).strftime('%d/%m/%Y %H:%M')
    metode_label = penarikan.metode
    info_data = [
        ['No. Penarikan', f'#{penarikan.id}'],
        ['Tanggal', tgl],
        ['Nasabah', penarikan.nasabah.nama_lengkap],
        ['Status', penarikan.get_status_display()],
        ['Metode', metode_label],
    ]
    if penarikan.nama_bank:
        info_data.append(['Bank', penarikan.nama_bank])
    if penarikan.no_rekening:
        info_data.append(['No. Rekening', penarikan.no_rekening])
    if penarikan.nama_pemilik_rekening:
        info_data.append(['Nama Pemilik', penarikan.nama_pemilik_rekening])

    info_table = Table(info_data, colWidths=[50 * mm, 80 * mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 5 * mm))

    # Nominal
    nominal_data = [
        ['Nominal Penarikan', _format_rupiah(penarikan.nominal)],
    ]
    nominal_table = Table(nominal_data, colWidths=[50 * mm, 80 * mm])
    nominal_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
    ]))
    elements.append(nominal_table)
    elements.append(Spacer(1, 5 * mm))

    # Footer
    elements.append(Paragraph(
        f'Dicetak: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
        normal_style,
    ))
    elements.append(Paragraph(
        'Penarikan diproses sesuai prosedur operasional MIRU Bank Sampah.',
        normal_style,
    ))

    doc.build(elements)
    return buf.getvalue()
