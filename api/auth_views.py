import secrets

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework_simplejwt.exceptions import TokenError

from .throttles import LoginAnonRateThrottle, OtpAnonRateThrottle

from .models import PasswordResetToken, PhoneOTP, PoinTransaksi, User
from .openapi import (
    auth_login_schema,
    auth_me_get_schema,
    auth_me_patch_schema,
    auth_refresh_schema,
)
from .serializers import UserProfileSerializer
from .services.whatsapp import (
    create_and_send_otp,
    mask_phone,
    otp_dev_response_extras,
    otp_request_message,
    phones_match,
    verify_otp_code,
)
from .utils.response import error_envelope, success_envelope, success_response


def user_auth_payload(user, request=None) -> dict:
    from api.services.object_storage import serialized_media_url

    return {
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'nama_lengkap': user.nama_lengkap,
        'no_hp': user.no_hp,
        'phone_verified': user.phone_verified,
        'saldo': str(user.saldo),
        'poin': user.poin,
        'avatar_url': serialized_media_url(user.avatar_url, request),
    }


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


class MiruTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = user_auth_payload(self.user, self.context.get('request'))
        return data


@auth_login_schema
class MiruTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = MiruTokenObtainPairSerializer
    throttle_classes = [LoginAnonRateThrottle]

    def post(self, request, *args, **kwargs):
        username = (request.data.get('username') or '').strip()
        password = request.data.get('password') or ''

        if not username or not password:
            return Response(
                error_envelope(
                    message='Username dan password wajib diisi.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code='VALIDATION_ERROR',
                    errors={
                        k: ['Wajib diisi.']
                        for k, v in (('username', username), ('password', password))
                        if not v
                    },
                    request=request,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                error_envelope(
                    message='Username tidak terdaftar.',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    code='AUTHENTICATION_FAILED',
                    errors={'username': ['Username tidak terdaftar.']},
                    request=request,
                ),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user_obj.check_password(password):
            return Response(
                error_envelope(
                    message='Password salah.',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    code='AUTHENTICATION_FAILED',
                    errors={'password': ['Password salah.']},
                    request=request,
                ),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user_obj.is_active:
            return Response(
                error_envelope(
                    message=(
                        'Akun belum aktif. Verifikasi nomor HP terlebih dahulu '
                        'sebelum login.'
                    ),
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    code='AUTHENTICATION_FAILED',
                    errors={
                        'phone_verified': [
                            'Akun belum aktif. Selesaikan verifikasi OTP WhatsApp.',
                        ],
                    },
                    request=request,
                ),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Gunakan serializer JWT untuk terbitkan token
        serializer = self.get_serializer(data={
            'username': username,
            'password': password,
        })
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(
            success_envelope(
                data={
                    'access': data['access'],
                    'refresh': data['refresh'],
                    'user': data['user'],
                },
                message='Login berhasil.',
                status_code=status.HTTP_200_OK,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )


@auth_refresh_schema
class MiruTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response(
                error_envelope(
                    message='Token refresh tidak valid.',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    code='AUTHENTICATION_FAILED',
                    errors={'refresh': ['Token tidak valid atau sudah kedaluwarsa.']},
                    request=request,
                ),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        data = serializer.validated_data
        return Response(
            success_envelope(
                data={'access': data['access']},
                message='Token berhasil diperbarui.',
                status_code=status.HTTP_200_OK,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=['Auth'],
    summary='Lupa password — cek username',
    description=(
        'Langkah 1 reset password (T2). Username tidak terdaftar → 400 '
        '(tanpa token orphan). Jika terdaftar → kembalikan nomor HP tersamar '
        'untuk dikonfirmasi di langkah berikutnya.'
    ),
    request={
        'type': 'object',
        'properties': {
            'username': {'type': 'string', 'description': 'Username akun'},
        },
        'required': ['username'],
    },
)
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginAnonRateThrottle]

    def post(self, request):
        username = (request.data.get('username') or '').strip()
        if not username:
            return _validation_error(
                request,
                'Username wajib diisi.',
                {'username': ['Username wajib diisi.']},
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Temuan T2: jangan sukses palsu / jangan buat token orphan
            return Response(
                error_envelope(
                    message='Username tidak terdaftar.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    code='NOT_FOUND',
                    errors={'username': ['Username tidak terdaftar.']},
                    request=request,
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        if not user.no_hp:
            return _validation_error(
                request,
                'Nomor HP belum terdaftar pada akun ini. Hubungi admin.',
                {'no_hp': ['Nomor HP belum terdaftar pada akun ini.']},
            )

        return Response(
            success_envelope(
                data={
                    'username': user.username,
                    'masked_phone': mask_phone(user.no_hp),
                    'next': 'confirm_phone',
                },
                message=(
                    'Username ditemukan. Konfirmasi nomor HP yang terdaftar, '
                    'lalu kami kirim kode OTP ke WhatsApp.'
                ),
                status_code=status.HTTP_200_OK,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=['Auth'],
    summary='Reset password — konfirmasi HP & kirim OTP WA',
    description=(
        'Langkah 2: nomor HP harus cocok dengan profil. OTP dikirim ke WhatsApp '
        '(stub/log jika WA_* belum diisi).'
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
class ResetPasswordRequestOtpView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OtpAnonRateThrottle]

    def post(self, request):
        username = (request.data.get('username') or '').strip()
        no_hp = (request.data.get('no_hp') or '').strip()
        if not username or not no_hp:
            errors = {}
            if not username:
                errors['username'] = ['Username wajib diisi.']
            if not no_hp:
                errors['no_hp'] = ['Nomor HP wajib diisi.']
            return _validation_error(request, 'Data tidak lengkap.', errors)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                error_envelope(
                    message='Username tidak terdaftar.',
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
            user, PhoneOTP.PURPOSE_PASSWORD_RESET, user.no_hp,
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
    summary='Reset password — verifikasi OTP',
    description=(
        'Langkah 3: verifikasi OTP. Jika valid, terbitkan reset_token '
        'untuk set password baru.'
    ),
    request={
        'type': 'object',
        'properties': {
            'username': {'type': 'string'},
            'otp': {'type': 'string'},
        },
        'required': ['username', 'otp'],
    },
)
class ResetPasswordVerifyOtpView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OtpAnonRateThrottle]

    def post(self, request):
        username = (request.data.get('username') or '').strip()
        otp_code = (request.data.get('otp') or '').strip()
        if not username or not otp_code:
            errors = {}
            if not username:
                errors['username'] = ['Username wajib diisi.']
            if not otp_code:
                errors['otp'] = ['Kode OTP wajib diisi.']
            return _validation_error(request, 'Data tidak lengkap.', errors)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                error_envelope(
                    message='Username tidak terdaftar.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    code='NOT_FOUND',
                    errors={'username': ['Username tidak terdaftar.']},
                    request=request,
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        verify_otp_code(user, PhoneOTP.PURPOSE_PASSWORD_RESET, otp_code)

        token = secrets.token_urlsafe(32)
        PasswordResetToken.objects.create(user=user, token=token)

        return Response(
            success_envelope(
                data={
                    'reset_token': token,
                    'expires_in': '1 hour',
                },
                message=(
                    'OTP berhasil diverifikasi. Gunakan reset_token untuk '
                    'mengatur password baru.'
                ),
                status_code=status.HTTP_200_OK,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=['Auth'],
    summary='Reset password — set password baru',
    description=(
        'Langkah 4: set password dengan password + password_confirm '
        '(min 6 karakter; sebaiknya beda dari password lama).'
    ),
    request={
        'type': 'object',
        'properties': {
            'token': {'type': 'string'},
            'password': {'type': 'string'},
            'password_confirm': {'type': 'string'},
            'new_password': {
                'type': 'string',
                'description': 'Alias legacy; prefer `password`.',
            },
        },
        'required': ['token', 'password', 'password_confirm'],
    },
)
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginAnonRateThrottle]

    def post(self, request):
        token_str = (request.data.get('token') or '').strip()
        password = request.data.get('password') or request.data.get('new_password') or ''
        password_confirm = request.data.get('password_confirm')
        if password_confirm is None and request.data.get('new_password'):
            # Legacy single-field clients: treat as confirmed
            password_confirm = password

        if not token_str:
            return _validation_error(
                request, 'Token wajib diisi.', {'token': ['Token wajib diisi.']},
            )

        if len(password) < 6:
            return _validation_error(
                request,
                'Password minimal 6 karakter.',
                {'password': ['Password minimal 6 karakter.']},
            )

        if password_confirm is None:
            return _validation_error(
                request,
                'Konfirmasi password wajib diisi.',
                {'password_confirm': ['Konfirmasi password wajib diisi.']},
            )

        if password != password_confirm:
            return _validation_error(
                request,
                'Password dan konfirmasi tidak sama.',
                {'password_confirm': ['Password dan konfirmasi tidak sama.']},
            )

        try:
            token = PasswordResetToken.objects.get(
                token=token_str, is_used=False,
            )
        except PasswordResetToken.DoesNotExist:
            return Response(
                error_envelope(
                    message='Token tidak valid atau sudah digunakan.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code='TOKEN_INVALID',
                    errors={'token': ['Token tidak valid atau sudah digunakan.']},
                    request=request,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        if token.is_expired:
            return Response(
                error_envelope(
                    message='Token sudah kedaluwarsa (masa berlaku 1 jam).',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code='TOKEN_EXPIRED',
                    errors={'token': ['Token sudah kedaluwarsa.']},
                    request=request,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = token.user
        if user.check_password(password):
            return _validation_error(
                request,
                'Password baru harus berbeda dari password lama.',
                {'password': ['Password baru harus berbeda dari password lama.']},
            )

        user.set_password(password)
        user.save(update_fields=['password'])

        token.is_used = True
        token.save(update_fields=['is_used'])

        return Response(
            success_envelope(
                data={'username': user.username},
                message=(
                    'Password berhasil direset. Silakan login dengan password baru.'
                ),
                status_code=status.HTTP_200_OK,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=['Auth'],
    summary='Registrasi / verifikasi HP — minta OTP WA',
    description=(
        'Untuk registrasi: kirim username + no_hp (akun belum aktif). '
        'Untuk verifikasi ulang (login): user terautentikasi boleh kirim no_hp.'
    ),
    request={
        'type': 'object',
        'properties': {
            'username': {'type': 'string'},
            'no_hp': {'type': 'string'},
        },
        'required': ['no_hp'],
    },
)
class PhoneRequestOtpView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OtpAnonRateThrottle]

    def post(self, request):
        no_hp = (request.data.get('no_hp') or '').strip()
        username = (request.data.get('username') or '').strip()

        if not no_hp:
            return _validation_error(
                request, 'Nomor HP wajib diisi.', {'no_hp': ['Nomor HP wajib diisi.']},
            )

        user = None
        purpose = PhoneOTP.PURPOSE_PHONE_VERIFY

        if request.user and request.user.is_authenticated:
            user = request.user
            purpose = PhoneOTP.PURPOSE_PHONE_VERIFY
        elif username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response(
                    error_envelope(
                        message='Username tidak terdaftar.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        code='NOT_FOUND',
                        errors={'username': ['Username tidak terdaftar.']},
                        request=request,
                    ),
                    status=status.HTTP_404_NOT_FOUND,
                )
            if not user.is_active or not user.phone_verified:
                purpose = PhoneOTP.PURPOSE_REGISTRATION
            else:
                # Sudah aktif: hanya boleh ganti/verifikasi jika no_hp cocok
                # atau menyimpan nomor baru sebelum verifikasi
                purpose = PhoneOTP.PURPOSE_PHONE_VERIFY
        else:
            return _validation_error(
                request,
                'Username wajib diisi (atau login terlebih dahulu).',
                {'username': ['Username wajib diisi.']},
            )

        # Simpan nomor sementara pada profil jika belum / sedang registrasi
        if purpose == PhoneOTP.PURPOSE_REGISTRATION or not user.no_hp:
            user.no_hp = no_hp
            user.phone_verified = False
            user.save(update_fields=['no_hp', 'phone_verified'])
        elif not phones_match(no_hp, user.no_hp):
            # Ganti nomor → unverified
            user.no_hp = no_hp
            user.phone_verified = False
            user.save(update_fields=['no_hp', 'phone_verified'])

        create_and_send_otp(user, purpose, no_hp)
        return Response(
            success_envelope(
                data={
                    'username': user.username,
                    'masked_phone': mask_phone(no_hp),
                    'purpose': purpose,
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
    summary='Registrasi / verifikasi HP — verifikasi OTP',
    description=(
        'Verifikasi OTP HP. Untuk registrasi: aktifkan akun + phone_verified. '
        'Untuk user login: set phone_verified=true.'
    ),
    request={
        'type': 'object',
        'properties': {
            'username': {'type': 'string'},
            'otp': {'type': 'string'},
            'no_hp': {'type': 'string'},
        },
        'required': ['otp'],
    },
)
class PhoneVerifyOtpView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OtpAnonRateThrottle]

    def post(self, request):
        otp_code = (request.data.get('otp') or '').strip()
        username = (request.data.get('username') or '').strip()
        no_hp = (request.data.get('no_hp') or '').strip()

        if not otp_code:
            return _validation_error(
                request, 'Kode OTP wajib diisi.', {'otp': ['Kode OTP wajib diisi.']},
            )

        if request.user and request.user.is_authenticated:
            user = request.user
        elif username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response(
                    error_envelope(
                        message='Username tidak terdaftar.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        code='NOT_FOUND',
                        errors={'username': ['Username tidak terdaftar.']},
                        request=request,
                    ),
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return _validation_error(
                request,
                'Username wajib diisi (atau login terlebih dahulu).',
                {'username': ['Username wajib diisi.']},
            )

        # Coba purpose registrasi dulu, lalu phone_verify
        last_otp = (
            PhoneOTP.objects.filter(user=user, is_used=False)
            .order_by('-created_at')
            .first()
        )
        purpose = (
            last_otp.purpose if last_otp
            else PhoneOTP.PURPOSE_PHONE_VERIFY
        )
        verify_otp_code(user, purpose, otp_code)

        update_fields = ['phone_verified']
        user.phone_verified = True
        if no_hp and not phones_match(no_hp, user.no_hp):
            user.no_hp = no_hp
            update_fields.append('no_hp')
        if purpose == PhoneOTP.PURPOSE_REGISTRATION or not user.is_active:
            user.is_active = True
            update_fields.append('is_active')
        user.save(update_fields=update_fields)

        return Response(
            success_envelope(
                data={
                    'username': user.username,
                    'phone_verified': True,
                    'is_active': user.is_active,
                    'no_hp': user.no_hp,
                },
                message='Nomor HP berhasil diverifikasi. Silakan login.',
                status_code=status.HTTP_200_OK,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )


@extend_schema_view(get=auth_me_get_schema, patch=auth_me_patch_schema)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(
            request.user, context={'request': request},
        )
        return success_response(
            data=serializer.data,
            message='Profil berhasil diambil.',
            request=request,
        )

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response(
                error_envelope(
                    message='Satu atau lebih field tidak valid.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code='VALIDATION_ERROR',
                    errors={
                        field: [str(m) for m in msgs]
                        for field, msgs in serializer.errors.items()
                    },
                    request=request,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return success_response(
            data=serializer.data,
            message='Profil berhasil diperbarui.',
            request=request,
        )


@extend_schema(
    tags=['Auth'],
    summary='Informasi poin & masa berlaku',
    description=(
        'Menampilkan saldo poin, total poin yang akan hangus, '
        'dan tanggal kedaluwarsa terdekat (Fase 8.5).'
    ),
)
class PoinInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()

        # Total poin aktif
        poin_aktif = PoinTransaksi.objects.filter(
            user=user, is_expired=False, sisa__gt=0,
        )

        total_akan_hangus = 0
        tanggal_kedaluwarsa_terdekat = None

        for pt in poin_aktif:
            total_akan_hangus += pt.sisa
            if (
                tanggal_kedaluwarsa_terdekat is None
                or pt.tanggal_kedaluwarsa < tanggal_kedaluwarsa_terdekat
            ):
                tanggal_kedaluwarsa_terdekat = pt.tanggal_kedaluwarsa

        return success_response(
            data={
                'poin_saat_ini': user.poin,
                'total_akan_hangus': total_akan_hangus,
                'tanggal_kedaluwarsa_terdekat': (
                    tanggal_kedaluwarsa_terdekat.isoformat()
                    if tanggal_kedaluwarsa_terdekat
                    else None
                ),
                'catatan': (
                    'Poin berlaku 1 tahun sejak diperoleh. '
                    'Poin yang tidak digunakan akan hangus otomatis.'
                ),
            },
            message='Informasi poin berhasil diambil.',
            request=request,
        )
