"""
Views for downloading KTP lampiran (pending only) and PDF receipts (role-gated).
"""

import mimetypes

from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import AuditLog, PenarikanSaldo, TransaksiSetoran
from rest_framework import status
from rest_framework.response import Response

from .permissions import IsAdminOrKoordinator
from .services.pdf_receipt import (
    generate_deposit_receipt,
    generate_withdrawal_receipt,
)
from .utils.response import error_envelope


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class DownloadLampiranKTPView(APIView):
    """
    Unduh lampiran KTP penarikan besar — hanya selama status menunggu.

    Setelah approve/tolak file dihapus. Hanya admin/koordinator.
    """

    permission_classes = [IsAuthenticated, IsAdminOrKoordinator]

    def get(self, request, withdrawal_id):
        penarikan = get_object_or_404(PenarikanSaldo, pk=withdrawal_id)
        if penarikan.status != 'menunggu' or not penarikan.lampiran_ktp:
            return Response(
                error_envelope(
                    message=(
                        'Lampiran KTP tidak tersedia. '
                        'File hanya ada saat pengajuan menunggu verifikasi.'
                    ),
                    status_code=status.HTTP_404_NOT_FOUND,
                    code='NOT_FOUND',
                    errors={'lampiran_ktp': ['Tidak tersedia.']},
                    request=request,
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        file_path = penarikan.lampiran_ktp.path
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'

        AuditLog.objects.create(
            user=request.user,
            action='view',
            model_name='PenarikanSaldo',
            object_id=str(penarikan.pk),
            changes={'lampiran_ktp': {'old': None, 'new': 'diakses'}},
            ip_address=_client_ip(request),
        )

        from io import BytesIO

        with open(file_path, 'rb') as fh:
            payload = BytesIO(fh.read())

        response = FileResponse(
            payload,
            content_type=content_type,
        )
        response['Content-Disposition'] = (
            f'attachment; filename="verifikasi_penarikan_{penarikan.id}.jpg"'
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
