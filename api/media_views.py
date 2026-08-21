"""Unggah & sajikan objek publik (gambar edukasi)."""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import FileResponse, Http404
from django.views import View
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .openapi import MEDIA_TAG

from .serializers import MediaUploadSerializer
from .services.object_storage import (
    ObjectNotFound,
    open_public_object,
    public_object_url,
    save_public_image,
)
from .utils.response import success_response


class MediaUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=[MEDIA_TAG],
        summary='Unggah gambar publik (WebP)',
        description=(
            'Unggah gambar ke MinIO. Server mengonversi ke WebP sebelum disimpan. '
            '`purpose=edukasi` atau `konten` hanya admin/koordinator; '
            '`purpose=avatar` untuk semua user login.'
        ),
        request=MediaUploadSerializer,
        examples=[
            OpenApiExample(
                'Unggah gambar edukasi',
                value={'purpose': 'edukasi'},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = MediaUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        purpose = serializer.validated_data['purpose']
        role = getattr(request.user, 'role', None)
        if purpose in ('edukasi', 'konten') and role not in ('admin', 'koordinator'):
            raise PermissionDenied(
                'Hanya admin/koordinator yang dapat mengunggah gambar konten.'
            )
        try:
            stored = save_public_image(
                serializer.validated_data['file'],
                purpose=serializer.validated_data['purpose'],
            )
        except DjangoValidationError as exc:
            raise DRFValidationError({'file': exc.messages}) from exc
        return success_response(
            data={
                'key': stored['key'],
                'url': public_object_url(stored['key'], request),
                'content_type': stored['content_type'],
                'size': stored['size'],
            },
            message='Gambar berhasil diunggah.',
            status_code=201,
            request=request,
        )


class PublicObjectView(View):
    """GET /objects/<key> — gambar edukasi publik (tanpa auth)."""

    def get(self, request, key):
        try:
            stream, content_type, length = open_public_object(key)
        except ObjectNotFound:
            raise Http404('Objek tidak ditemukan.') from None
        response = FileResponse(stream, content_type=content_type)
        if length is not None:
            response['Content-Length'] = str(length)
        response['Cache-Control'] = 'public, max-age=604800'
        return response
