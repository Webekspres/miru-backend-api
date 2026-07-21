import secrets
import uuid

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework_simplejwt.exceptions import TokenError

from .throttles import LoginAnonRateThrottle

from .models import PasswordResetToken, PoinTransaksi, User
from .openapi import (
    auth_login_schema,
    auth_me_get_schema,
    auth_me_patch_schema,
    auth_refresh_schema,
)
from .serializers import UserProfileSerializer
from .utils.response import error_envelope, success_envelope, success_response


def user_auth_payload(user) -> dict:
    return {
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'nama_lengkap': user.nama_lengkap,
        'no_hp': user.no_hp,
        'saldo': str(user.saldo),
        'poin': user.poin,
    }


class MiruTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = user_auth_payload(self.user)
        return data


@auth_login_schema
class MiruTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = MiruTokenObtainPairSerializer
    throttle_classes = [LoginAnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            errors = {
                field: [str(m) for m in msgs]
                for field, msgs in serializer.errors.items()
            }
            return Response(
                error_envelope(
                    message='Username atau password salah.',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    code='AUTHENTICATION_FAILED',
                    errors=errors,
                    request=request,
                ),
                status=status.HTTP_401_UNAUTHORIZED,
            )

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
    summary='Lupa password — minta token reset',
    description=(
        'Kirim username untuk mendapatkan token reset password. '
        'Token dikembalikan di response (karena belum ada email/SMS). '
        'Masa berlaku token 1 jam.'
    ),
    request={
        'type': 'object',
        'properties': {
            'username': {'type': 'string', 'description': 'Username akun'},
        },
        'required': ['username'],
    },
    responses={
        200: {'type': 'object', 'properties': {
            'success': {'type': 'boolean'},
            'message': {'type': 'string'},
            'data': {'type': 'object', 'properties': {
                'reset_token': {'type': 'string'},
                'expires_in': {'type': 'string'},
            }},
        }},
    },
)
class ForgotPasswordView(APIView):
    """
    Endpoint lupa password.
    Menghasilkan token reset 1 jam dan mengembalikannya.
    Di production, token ini akan dikirim via email/SMS.
    """
    permission_classes = [AllowAny]
    throttle_classes = [LoginAnonRateThrottle]

    def post(self, request):
        username = request.data.get('username', '').strip()
        if not username:
            return Response(
                error_envelope(
                    message='Username wajib diisi.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code='VALIDATION_ERROR',
                    errors={'username': ['Username wajib diisi.']},
                    request=request,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Jangan ungkap apakah username ada atau tidak
            return Response(
                success_envelope(
                    data={'reset_token': None},
                    message='Jika username terdaftar, token reset akan dikirim.',
                    status_code=status.HTTP_200_OK,
                    request=request,
                ),
                status=status.HTTP_200_OK,
            )

        # Generate token unik
        token = secrets.token_urlsafe(32)
        PasswordResetToken.objects.create(
            user=user,
            token=token,
        )

        # Log token untuk dev (di production, kirim via email/SMS)
        import logging
        logger = logging.getLogger('miru.request')
        logger.info(
            'Password reset token for %s: %s (expires in 1 hour)',
            user.username, token,
        )

        return Response(
            success_envelope(
                data={
                    'reset_token': token,
                    'expires_in': '1 hour',
                },
                message=(
                    'Token reset password berhasil dibuat. '
                    'Gunakan token ini untuk mereset password Anda.'
                ),
                status_code=status.HTTP_200_OK,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=['Auth'],
    summary='Reset password menggunakan token',
    description=(
        'Gunakan token dari endpoint forgot-password untuk mereset password. '
        'Token hanya berlaku 1 jam dan hanya bisa dipakai sekali.'
    ),
    request={
        'type': 'object',
        'properties': {
            'token': {'type': 'string', 'description': 'Token reset password'},
            'new_password': {'type': 'string', 'description': 'Password baru (min 6 karakter)'},
        },
        'required': ['token', 'new_password'],
    },
)
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token_str = request.data.get('token', '').strip()
        new_password = request.data.get('new_password', '')

        if not token_str:
            return Response(
                error_envelope(
                    message='Token wajib diisi.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code='VALIDATION_ERROR',
                    errors={'token': ['Token wajib diisi.']},
                    request=request,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_password) < 6:
            return Response(
                error_envelope(
                    message='Password minimal 6 karakter.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code='VALIDATION_ERROR',
                    errors={'new_password': ['Password minimal 6 karakter.']},
                    request=request,
                ),
                status=status.HTTP_400_BAD_REQUEST,
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

        # Reset password
        user = token.user
        user.set_password(new_password)
        user.save(update_fields=['password'])

        # Tandai token sebagai sudah digunakan
        token.is_used = True
        token.save(update_fields=['is_used'])

        return Response(
            success_envelope(
                data={'username': user.username},
                message='Password berhasil direset. Silakan login dengan password baru.',
                status_code=status.HTTP_200_OK,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )


@extend_schema_view(get=auth_me_get_schema, patch=auth_me_patch_schema)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
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
