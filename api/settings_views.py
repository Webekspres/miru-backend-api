from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from .models import Pengumuman
from .openapi import SETTINGS_TAG, pengumuman_list_schema, settings_schema
from .permissions import IsAdmin
from .serializers import PengaturanInstitusiSerializer, PengumumanSerializer
from .services.settings import get_institution_settings
from .utils.pagination import MiruPagination
from .utils.response import success_response


@settings_schema
class InstitutionSettingsView(APIView):
    """GET public — profil institusi. PATCH admin only."""

    def get_permissions(self):
        # Do not override get_authenticators based on self.request —
        # schema generation calls it before request is bound (breaks /api/docs/).
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]

    def get(self, request):
        settings = get_institution_settings()
        serializer = PengaturanInstitusiSerializer(settings)
        return success_response(
            data=serializer.data,
            message='Pengaturan institusi berhasil diambil.',
            request=request,
        )

    @extend_schema(
        tags=[SETTINGS_TAG],
        summary='Perbarui pengaturan institusi (admin only)',
        request=PengaturanInstitusiSerializer,
    )
    def patch(self, request):
        settings = get_institution_settings()
        serializer = PengaturanInstitusiSerializer(
            settings, data=request.data, partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=serializer.data,
            message='Pengaturan institusi berhasil diperbarui.',
            request=request,
        )


@pengumuman_list_schema
class PengumumanListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Pengumuman.objects.filter(aktif=True)
        paginator = MiruPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = PengumumanSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


@extend_schema(
    tags=[SETTINGS_TAG],
    summary='Kebijakan data pribadi (UU PDP)',
    description=(
        'Dokumentasi data yang disimpan, retensi 5 tahun, hak pengguna, '
        'dan evaluasi keamanan data sensitif (NIK).'
    ),
)
class PrivacyPolicyView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        from .services.privacy_policy import get_privacy_policy
        return success_response(
            data=get_privacy_policy(),
            message='Kebijakan data pribadi berhasil diambil.',
            request=request,
        )


@extend_schema(
    tags=[SETTINGS_TAG],
    summary='Syarat dan ketentuan layanan',
    description=(
        'Dokumen syarat penggunaan aplikasi MIRU-G untuk Play Store '
        'dan situs web publik.'
    ),
)
class TermsOfServiceView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        from .services.privacy_policy import get_terms_of_service
        return success_response(
            data=get_terms_of_service(),
            message='Syarat dan ketentuan berhasil diambil.',
            request=request,
        )
