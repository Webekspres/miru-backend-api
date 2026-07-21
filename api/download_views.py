"""
Views for downloading KTP images and PDF receipts (role-gated).
Fase 8.4 — Identitas, lupa password, KTP.
"""

import mimetypes

from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import PenarikanSaldo, TransaksiSetoran, User
from rest_framework import status
from rest_framework.response import Response

from .permissions import IsAdminOrKoordinator
from .services.pdf_receipt import (
    generate_deposit_receipt,
    generate_withdrawal_receipt,
)
from .utils.response import error_envelope


class DownloadKTPView(APIView):
    """
    Role-gated download foto KTP nasabah.

    Hanya admin/koordinator yang bisa mengunduh KTP.
    URL tidak publik — query parameter tidak cukup, harus via header Authorization.
    """

    permission_classes = [IsAuthenticated, IsAdminOrKoordinator]

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        if not user.foto_ktp:
            return Response(
                error_envelope(
                    message='Nasabah ini belum mengunggah foto KTP.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    code='NOT_FOUND',
                    errors={'foto_ktp': ['Belum diunggah.']},
                    request=request,
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        file_path = user.foto_ktp.path
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'

        response = FileResponse(
            open(file_path, 'rb'),
            content_type=content_type,
        )
        response['Content-Disposition'] = (
            f'attachment; filename="KTP_{user.nama_lengkap}_{user.id}.jpg"'
        )
        return response


class DownloadLampiranKTPView(APIView):
    """
    Role-gated download lampiran KTP pada penarikan besar.

    Hanya admin/koordinator yang bisa mengunduh.
    """

    permission_classes = [IsAuthenticated, IsAdminOrKoordinator]

    def get(self, request, withdrawal_id):
        penarikan = get_object_or_404(PenarikanSaldo, pk=withdrawal_id)
        if not penarikan.lampiran_ktp:
            return Response(
                error_envelope(
                    message='Penarikan ini tidak memiliki lampiran KTP.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    code='NOT_FOUND',
                    errors={'lampiran_ktp': ['Belum diunggah.']},
                    request=request,
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        file_path = penarikan.lampiran_ktp.path
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'

        response = FileResponse(
            open(file_path, 'rb'),
            content_type=content_type,
        )
        response['Content-Disposition'] = (
            f'attachment; filename="LampiranKTP_Penarikan_{penarikan.id}.jpg"'
        )
        return response


class DownloadDepositReceiptView(APIView):
    """
    Download PDF bukti setoran. Role-gated:
    - Nasabah → hanya unduh milik sendiri
    - Admin/koordinator/petugas → unduh semua
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, deposit_id):
        transaksi = get_object_or_404(TransaksiSetoran, pk=deposit_id)

        # Nasabah hanya bisa unduh bukti milik sendiri
        if request.user.role == 'nasabah' and transaksi.nasabah_id != request.user.id:
            return Response(
                error_envelope(
                    message='Anda tidak memiliki akses ke bukti setoran ini.',
                    status_code=status.HTTP_403_FORBIDDEN,
                    code='FORBIDDEN',
                    errors={'akses': ['Bukan milik Anda.']},
                    request=request,
                ),
                status=status.HTTP_403_FORBIDDEN,
            )

        pdf_bytes = generate_deposit_receipt(transaksi)
        filename = f'bukti_setoran_{transaksi.id}.pdf'

        return HttpResponse(pdf_bytes, content_type='application/pdf', headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(len(pdf_bytes)),
        })


class DownloadWithdrawalReceiptView(APIView):
    """
    Download PDF tanda terima penarikan. Role-gated:
    - Nasabah → hanya unduh milik sendiri
    - Admin/koordinator → unduh semua
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, withdrawal_id):
        penarikan = get_object_or_404(PenarikanSaldo, pk=withdrawal_id)

        # Nasabah hanya bisa unduh milik sendiri
        if request.user.role == 'nasabah' and penarikan.nasabah_id != request.user.id:
            return Response(
                error_envelope(
                    message='Anda tidak memiliki akses ke tanda terima ini.',
                    status_code=status.HTTP_403_FORBIDDEN,
                    code='FORBIDDEN',
                    errors={'akses': ['Bukan milik Anda.']},
                    request=request,
                ),
                status=status.HTTP_403_FORBIDDEN,
            )

        pdf_bytes = generate_withdrawal_receipt(penarikan)
        filename = f'tanda_terima_penarikan_{penarikan.id}.pdf'

        return HttpResponse(pdf_bytes, content_type='application/pdf', headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(len(pdf_bytes)),
        })
