from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .utils.response import error_envelope, success_envelope


class MiruTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'role': self.user.role,
            'nama_lengkap': self.user.nama_lengkap,
        }
        return data


class MiruTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = MiruTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            errors = {}
            for field, msgs in serializer.errors.items():
                errors[field] = [str(m) for m in msgs]
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


class MiruTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            errors = {}
            for field, msgs in serializer.errors.items():
                errors[field] = [str(m) for m in msgs]
            return Response(
                error_envelope(
                    message='Token refresh tidak valid.',
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
                data={'access': data['access']},
                message='Token berhasil diperbarui.',
                status_code=status.HTTP_200_OK,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )
