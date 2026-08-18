"""
Self-service hapus akun nasabah — kewajiban Play Store.

Alur (konfirmasi mendalam, validasi OTP WhatsApp seperti saat login):
1. `check`          — username → ringkasan akun + nomor HP tersamar.
2. `request-otp`    — username + nomor HP lengkap (harus cocok) → kirim OTP WA.
3. `confirm`        — username + OTP + ketik konfirmasi + centang pemahaman
                      → verifikasi OTP lalu anonimkan & nonaktifkan akun.

Ketiga endpoint publik (tanpa login) karena nasabah tidak login ke panel web.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import (
    PenarikanSaldo,
    Pengaduan,
    Penjemputan,
    PenukaranPoin,
    PhoneOTP,
    TransaksiSetoran,
    User,
)
from .services.account_deletion import delete_nasabah_account
from .services.whatsapp import (
    create_and_send_otp,
    mask_phone,
    otp_dev_response_extras,
    otp_request_message,
    phones_match,
    verify_otp_code,
)
from .throttles import OtpAnonRateThrottle
from .utils.response import error_envelope, success_envelope

# Teks yang harus diketik user pada langkah konfirmasi akhir.
CONFIRMATION_PHRASES = ('HAPUS', 'HAPUS AKUN')


def _validation_error(request, message, errors, status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        error_envelope(
            message=message,
            status_code=status_code,
            code='VALIDATION_ERROR',
            errors=errors,
            request=request,
        ),
        status=status_code,
    )


def _get_nasabah_for_deletion(request, username: str):
    """Cari user untuk proses hapus akun; kembalikan (user, error_response)."""
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None, None

    if not user.is_active or user.username.startswith('deleted_'):
        return None, None

    if user.role != 'nasabah':
        return None, _validation_error(
            request,
            'Akun staf dikelola oleh admin. Hubungi admin untuk penghapusan akun.',
            {'username': ['Hanya akun nasabah yang dapat dihapus melalui halaman ini.']},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not user.no_hp:
        return None, _validation_error(
            request,
            'Nomor HP belum terdaftar pada akun ini. Hubungi admin.',
            {'no_hp': ['Nomor HP belum terdaftar pada akun ini.']},
        )

    return user, None


@extend_schema(
    tags=['Auth'],
    summary='Hapus akun — cek username & ringkasan data',
    description=(
        'Langkah 1: masukkan username. Jika terdaftar, kembalikan ringkasan '
        'akun (nama, nomor HP tersamar, saldo, poin, jumlah riwayat) agar '
        'user tahu persis apa yang akan hilang sebelum menghapus.'
    ),
    request={
        'type': 'object',
        'properties': {
            'username': {'type': 'string', 'description': 'Username akun nasabah'},
        },
        'required': ['username'],
    },
)
class DeleteAccountCheckView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OtpAnonRateThrottle]

    def post(self, request):
        username = (request.data.get('username') or '').strip()
        if not username:
            return _validation_error(
                request,
                'Username wajib diisi.',
                {'username': ['Username wajib diisi.']},
            )

        user, error = _get_nasabah_for_deletion(request, username)
        if error is not None:
            return error
        if user is None:
            return Response(
                error_envelope(
                    message='Username tidak terdaftar atau akun sudah tidak aktif.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    code='NOT_FOUND',
                    errors={'username': ['Username tidak terdaftar.']},
                    request=request,
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            success_envelope(
                data={
                    'username': user.username,
                    'nama_lengkap': user.nama_lengkap,
                    'masked_phone': mask_phone(user.no_hp),
                    'saldo': str(user.saldo),
                    'poin': user.poin,
                    'riwayat': {
                        'jumlah_setoran': TransaksiSetoran.objects.filter(nasabah=user).count(),
                        'jumlah_penjemputan': Penjemputan.objects.filter(nasabah=user).count(),
                        'jumlah_penarikan': PenarikanSaldo.objects.filter(nasabah=user).count(),
                        'jumlah_penukaran_poin': PenukaranPoin.objects.filter(nasabah=user).count(),
                        'jumlah_pengaduan': Pengaduan.objects.filter(nasabah=user).count(),
                    },
                    'next': 'confirm_phone',
                },
                message=(
                    'Akun ditemukan. Konfirmasi nomor HP yang terdaftar, '
                    'lalu kami kirim kode OTP ke WhatsApp.'
                ),
                status_code=status.HTTP_200_OK,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=['Auth'],
    summary='Hapus akun — konfirmasi HP & kirim OTP WA',
    description=(
        'Langkah 2: nomor HP harus cocok dengan profil. OTP dikirim ke '
        'WhatsApp (stub/log jika WA_* belum diisi).'
    ),
    request={
        'type': 'object',
        'properties': {
            'username': {'type': 'string'},
            'no_hp': {'type': 'string'},
        },
        'required': ['username', 'no_hp'],
    },
)
class DeleteAccountRequestOtpView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OtpAnonRateThrottle]

    def post(self, request):
        username = (request.data.get('username') or '').strip()
        no_hp = (request.data.get('no_hp') or '').strip()

        errors = {}
        if not username:
            errors['username'] = ['Username wajib diisi.']
        if not no_hp:
            errors['no_hp'] = ['Nomor HP wajib diisi.']
        if errors:
            return _validation_error(request, 'Data tidak lengkap.', errors)

        user, error = _get_nasabah_for_deletion(request, username)
        if error is not None:
            return error
        if user is None:
            return Response(
                error_envelope(
                    message='Username tidak terdaftar atau akun sudah tidak aktif.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    code='NOT_FOUND',
                    errors={'username': ['Username tidak terdaftar.']},
                    request=request,
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        if not phones_match(no_hp, user.no_hp):
            return _validation_error(
                request,
                'Nomor HP tidak cocok dengan profil.',
                {'no_hp': ['Nomor HP tidak cocok dengan yang terdaftar.']},
            )

        create_and_send_otp(
            user, PhoneOTP.PURPOSE_ACCOUNT_DELETION, user.no_hp,
        )
        return Response(
            success_envelope(
                data={
                    'username': user.username,
                    'masked_phone': mask_phone(user.no_hp),
                    'expires_in_seconds': 300,
                    **otp_dev_response_extras(),
                },
                message=otp_request_message(
                    'Kode OTP telah dikirim ke WhatsApp Anda. '
                    'Periksa notifikasi WhatsApp.'
                ),
                status_code=status.HTTP_200_OK,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=['Auth'],
    summary='Hapus akun — verifikasi OTP & konfirmasi akhir',
    description=(
        'Langkah 3: verifikasi OTP + konfirmasi mendalam. `confirmation_text` '
        'harus sama dengan username (case-insensitive) atau salah satu dari '
        '"HAPUS" / "HAPUS AKUN", dan `acknowledge` harus true. Jika valid, '
        'akun dianonimkan & dinonaktifkan (data pribadi dihapus, riwayat '
        'transaksi dipertahankan untuk catatan keuangan bank sampah).'
    ),
    request={
        'type': 'object',
        'properties': {
            'username': {'type': 'string'},
            'otp': {'type': 'string'},
            'confirmation_text': {'type': 'string'},
            'acknowledge': {'type': 'boolean'},
        },
        'required': ['username', 'otp', 'confirmation_text', 'acknowledge'],
    },
)
class DeleteAccountConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OtpAnonRateThrottle]

    def post(self, request):
        username = (request.data.get('username') or '').strip()
        otp_code = (request.data.get('otp') or '').strip()
        confirmation_text = (request.data.get('confirmation_text') or '').strip()
        acknowledge = request.data.get('acknowledge')

        errors = {}
        if not username:
            errors['username'] = ['Username wajib diisi.']
        if not otp_code:
            errors['otp'] = ['Kode OTP wajib diisi.']
        if not confirmation_text:
            errors['confirmation_text'] = ['Ketik teks konfirmasi untuk melanjutkan.']
        if acknowledge is not True:
            errors['acknowledge'] = ['Anda harus mencentang pernyataan pemahaman.']
        if errors:
            return _validation_error(request, 'Data tidak lengkap.', errors)

        user, error = _get_nasabah_for_deletion(request, username)
        if error is not None:
            return error
        if user is None:
            return Response(
                error_envelope(
                    message='Username tidak terdaftar atau akun sudah tidak aktif.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    code='NOT_FOUND',
                    errors={'username': ['Username tidak terdaftar.']},
                    request=request,
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        # Konfirmasi mendalam: teks harus cocok dengan username atau frasa tetap.
        normalized = confirmation_text.upper().replace(' ', '')
        matches_username = normalized == user.username.upper().replace(' ', '')
        matches_phrase = normalized in {
            phrase.replace(' ', '') for phrase in CONFIRMATION_PHRASES
        }
        if not (matches_username or matches_phrase):
            return _validation_error(
                request,
                'Teks konfirmasi tidak sesuai.',
                {
                    'confirmation_text': [
                        'Ketik username Anda atau "HAPUS AKUN" untuk melanjutkan.',
                    ],
                },
            )

        # Verifikasi OTP — raise ValidationError → dirender envelope oleh
        # exception handler (sama seperti alur reset password).
        verify_otp_code(user, PhoneOTP.PURPOSE_ACCOUNT_DELETION, otp_code)

        delete_nasabah_account(user)

        return Response(
            success_envelope(
                data={'username_terhapus': username},
                message=(
                    'Permintaan penghapusan akun berhasil diproses. '
                    'Data pribadi Anda telah dihapus.'
                ),
                status_code=status.HTTP_200_OK,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )
