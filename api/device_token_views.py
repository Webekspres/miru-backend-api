"""Device token (FCM) registration endpoints — Fase 8.6."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import DeviceToken
from .openapi import NOTIFICATIONS_TAG
from .permissions import IsPemerintahReadOnly
from .serializers import DeviceTokenSerializer
from .utils.response import error_response, success_response


@extend_schema_view(
    create=extend_schema(
        tags=[NOTIFICATIONS_TAG],
        summary='Register FCM device token',
        description=(
            'Daftarkan atau perbarui FCM device token milik user yang login. '
            'Token yang sama dari device lain akan dipindahkan ke user ini.'
        ),
        request=DeviceTokenSerializer,
        responses={200: DeviceTokenSerializer, 201: DeviceTokenSerializer},
    ),
    destroy=extend_schema(
        tags=[NOTIFICATIONS_TAG],
        summary='Unregister FCM device token',
        description='Hapus device token milik user yang login (by token string di body atau pk).',
    ),
    list=extend_schema(
        tags=[NOTIFICATIONS_TAG],
        summary='Daftar device token milik user',
    ),
)
class DeviceTokenViewSet(viewsets.ViewSet):
    """
    Register / unregister FCM device tokens.

    - POST   /api/device-tokens/          { "token": "...", "platform": "android" }
    - GET    /api/device-tokens/          list milik user
    - DELETE /api/device-tokens/{pk}/     hapus by id (milik user)
    - DELETE /api/device-tokens/unregister/  body: { "token": "..." }
    """

    permission_classes = [IsAuthenticated, IsPemerintahReadOnly]

    def list(self, request):
        qs = DeviceToken.objects.filter(user=request.user).order_by('-updated_at')
        serializer = DeviceTokenSerializer(qs, many=True)
        return success_response(
            data=serializer.data,
            message='Daftar device token berhasil diambil.',
            request=request,
        )

    def create(self, request):
        serializer = DeviceTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        platform = serializer.validated_data.get('platform', 'android')

        obj, created = DeviceToken.objects.update_or_create(
            token=token,
            defaults={'user': request.user, 'platform': platform},
        )
        out = DeviceTokenSerializer(obj)
        return success_response(
            data=out.data,
            message=(
                'Device token berhasil didaftarkan.'
                if created
                else 'Device token berhasil diperbarui.'
            ),
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            request=request,
        )

    def destroy(self, request, pk=None):
        deleted, _ = DeviceToken.objects.filter(pk=pk, user=request.user).delete()
        if not deleted:
            return error_response(
                message='Device token tidak ditemukan.',
                status_code=status.HTTP_404_NOT_FOUND,
                code='NOT_FOUND',
                request=request,
            )
        return success_response(
            data=None,
            message='Device token berhasil dihapus.',
            request=request,
        )

    def unregister(self, request):
        """DELETE by token string (body) — praktis dari mobile logout."""
        token = request.data.get('token', '').strip()
        if not token:
            return error_response(
                message='Field token wajib diisi.',
                status_code=status.HTTP_400_BAD_REQUEST,
                code='VALIDATION_ERROR',
                request=request,
            )
        deleted, _ = DeviceToken.objects.filter(
            token=token, user=request.user,
        ).delete()
        if not deleted:
            return error_response(
                message='Device token tidak ditemukan.',
                status_code=status.HTTP_404_NOT_FOUND,
                code='NOT_FOUND',
                request=request,
            )
        return success_response(
            data=None,
            message='Device token berhasil dihapus.',
            request=request,
        )
