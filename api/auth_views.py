from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework_simplejwt.exceptions import TokenError

from .throttles import LoginAnonRateThrottle

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
