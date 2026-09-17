from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Notifikasi
from .openapi import NOTIFICATIONS_TAG, notification_schema
from .permissions import IsPemerintahReadOnly
from .querysets import READ_ALL_ROLES
from .serializers import NotifikasiSerializer
from .utils.pagination import MiruPagination
from .utils.response import success_response


@notification_schema
class NotifikasiViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk notifikasi in-app.

    - Nasabah & petugas hanya melihat notifikasi miliknya sendiri.
    - Admin/koordinator/pemerintah bisa melihat semua (atau filter ?user=).
    - Endpoint khusus:
      * `{id}/read/` — Tandai satu notifikasi sebagai sudah dibaca.
      * `mark-all-read/` — Tandai semua notifikasi user sebagai sudah dibaca.
    """

    queryset = Notifikasi.objects.select_related('user').all()
    serializer_class = NotifikasiSerializer
    pagination_class = MiruPagination
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    # POST dibutuhkan untuk mark_read / mark_all_read (actions).
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_permissions(self):
        # Semua role terautentikasi boleh baca/tandai notifikasi miliknya.
        return [IsAuthenticated(), IsPemerintahReadOnly()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role in ('nasabah', 'petugas'):
            return qs.filter(user=user)
        if user.role in READ_ALL_ROLES:
            user_id = self.request.query_params.get('user')
            if user_id:
                return qs.filter(user_id=user_id)
            return qs
        # Role lain (jika ada): hanya milik sendiri
        return qs.filter(user=user)

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return success_response(
            data=serializer.data,
            message='Daftar notifikasi berhasil diambil.',
            request=request,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message='Notifikasi berhasil diambil.',
            request=request,
        )

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        """Tandai satu notifikasi sebagai sudah dibaca."""
        instance = self.get_object()
        if not instance.is_read:
            instance.is_read = True
            instance.save(update_fields=['is_read'])
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message='Notifikasi ditandai sudah dibaca.',
            request=request,
        )

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """Tandai semua notifikasi milik user login sebagai sudah dibaca."""
        qs = Notifikasi.objects.filter(user=request.user, is_read=False)
        count = qs.update(is_read=True)
        return success_response(
            data={'updated_count': count},
            message=f'{count} notifikasi ditandai sudah dibaca.',
            request=request,
        )
