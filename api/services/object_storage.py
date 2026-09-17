"""Penyimpanan objek publik (gambar edukasi & avatar) — MinIO, fallback filesystem."""

from __future__ import annotations

import io
import os
import re
import uuid
from pathlib import Path

from botocore.client import Config
from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image, ImageOps
from rest_framework.request import Request

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
PURPOSE_CONFIG = {
    'edukasi': {'prefix': 'edukasi', 'max_px': 1600, 'quality': 82},
    'avatar': {'prefix': 'avatar', 'max_px': 512, 'quality': 80},
    'konten': {'prefix': 'konten', 'max_px': 1600, 'quality': 82},
}
MAX_UPLOAD_SIZE_MB = 5
MAX_UPLOAD_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
SAFE_OBJECT_KEY = re.compile(
    r'^(edukasi|avatar|konten)/[a-f0-9]{32}\.(jpe?g|png|gif|webp)$',
    re.IGNORECASE,
)
OBJECTS_MARKER = '/objects/'
_EXECUTABLE_MAGICS = {b'MZ', b'\x7fELF', b'\xca\xfe\xba\xbe', b'\xcf\xfa\xed\xfe'}
WEBP_CONTENT_TYPE = 'image/webp'


class ObjectNotFound(Exception):
    """Objek tidak ada di MinIO atau filesystem."""


def _is_allowed_image_header(header: bytes) -> bool:
    if header.startswith(b'\xff\xd8\xff'):
        return True
    if header.startswith(b'\x89PNG\r\n\x1a\n'):
        return True
    if header.startswith((b'GIF87a', b'GIF89a')):
        return True
    if header.startswith(b'RIFF') and header[8:12] == b'WEBP':
        return True
    return False


def validate_image_upload(uploaded) -> None:
    """Validasi tipe/ukuran gambar sebelum konversi WebP."""
    name = getattr(uploaded, 'name', '') or 'upload.jpg'
    ext = os.path.splitext(name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'Format file tidak didukung. Gunakan: {", ".join(sorted(ALLOWED_IMAGE_EXTENSIONS))}.'
        )
    size = getattr(uploaded, 'size', 0) or 0
    if size > MAX_UPLOAD_BYTES:
        raise ValidationError(f'Ukuran file maksimal {MAX_UPLOAD_SIZE_MB} MB.')
    header = uploaded.read(16)
    uploaded.seek(0)
    if header[:2] in {b'MZ', b'\x7f\x45'} or header[:4] in _EXECUTABLE_MAGICS:
        raise ValidationError('File executable tidak diizinkan untuk diunggah.')
    if len(header) < 12 or not _is_allowed_image_header(header):
        raise ValidationError('File bukan gambar yang valid (JPEG, PNG, GIF, atau WebP).')


def to_webp_bytes(uploaded, *, max_px: int, quality: int) -> bytes:
    """Konversi unggahan ke WebP (frame pertama bila animasi)."""
    uploaded.seek(0)
    try:
        with Image.open(uploaded) as im:
            im = ImageOps.exif_transpose(im)
            if getattr(im, 'n_frames', 1) > 1:
                im.seek(0)
                im = im.copy()
            if im.mode not in ('RGB', 'RGBA'):
                im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
            im.thumbnail((max_px, max_px), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format='WEBP', quality=quality, method=6)
            return buf.getvalue()
    except (OSError, ValueError) as exc:
        raise ValidationError('File gambar tidak dapat diproses.') from exc


def normalize_stored_media_ref(value: str | None) -> str:
    """Simpan key objek bila URL berasal dari /objects/; URL eksternal tetap utuh."""
    value = (value or '').strip()
    if not value:
        return ''
    if OBJECTS_MARKER in value:
        return value.split(OBJECTS_MARKER, 1)[1].split('?', 1)[0]
    return value


def public_object_url(key_or_url: str, request: Request | None = None) -> str:
    value = (key_or_url or '').strip()
    if not value:
        return ''
    if value.startswith(('http://', 'https://')):
        return value
    if settings.MINIO_PUBLIC_URL:
        return f'{settings.MINIO_PUBLIC_URL}/{value.lstrip("/")}'
    path = f'{OBJECTS_MARKER}{value.lstrip("/")}'
    if request is not None:
        return request.build_absolute_uri(path)
    return path


def serialized_media_url(stored: str | None, request=None) -> str | None:
    return public_object_url(stored or '', request) or None


def _s3_client():
    import boto3

    return boto3.client(
        's3',
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        region_name=settings.MINIO_REGION,
        config=Config(signature_version='s3v4', s3={'addressing_style': 'path'}),
    )


def ensure_bucket() -> None:
    """Buat bucket MinIO bila belum ada (dev lokal tanpa Docker)."""
    if not settings.MINIO_ENABLED:
        return
    from botocore.exceptions import ClientError

    client = _s3_client()
    bucket = settings.MINIO_BUCKET
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError:
        client.create_bucket(Bucket=bucket)


def clear_public_prefixes() -> int:
    """Hapus objek di folder avatar/ dan edukasi/ (MinIO atau MEDIA_ROOT)."""
    deleted = 0
    prefixes = tuple(f"{cfg['prefix']}/" for cfg in PURPOSE_CONFIG.values())
    if settings.MINIO_ENABLED:
        client = _s3_client()
        paginator = client.get_paginator('list_objects_v2')
        for prefix in prefixes:
            for page in paginator.paginate(
                Bucket=settings.MINIO_BUCKET, Prefix=prefix,
            ):
                keys = [{'Key': obj['Key']} for obj in page.get('Contents', [])]
                if not keys:
                    continue
                client.delete_objects(
                    Bucket=settings.MINIO_BUCKET,
                    Delete={'Objects': keys},
                )
                deleted += len(keys)
        return deleted

    import shutil

    for prefix in ('avatar', 'edukasi', 'konten'):
        dest = Path(settings.MEDIA_ROOT) / prefix
        if dest.is_dir():
            shutil.rmtree(dest)
            deleted += 1
    return deleted


def save_public_image(uploaded, *, purpose: str = 'edukasi') -> dict:
    """Validasi, konversi WebP, lalu simpan. Return dict key, content_type, size."""
    config = PURPOSE_CONFIG.get(purpose)
    if config is None:
        raise ValidationError('Tujuan unggah tidak dikenali.')
    validate_image_upload(uploaded)
    payload = to_webp_bytes(
        uploaded,
        max_px=config['max_px'],
        quality=config['quality'],
    )
    key = f"{config['prefix']}/{uuid.uuid4().hex}.webp"

    if settings.MINIO_ENABLED:
        client = _s3_client()
        client.put_object(
            Bucket=settings.MINIO_BUCKET,
            Key=key,
            Body=payload,
            ContentType=WEBP_CONTENT_TYPE,
        )
    else:
        dest = Path(settings.MEDIA_ROOT) / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(payload)

    return {
        'key': key,
        'content_type': WEBP_CONTENT_TYPE,
        'size': len(payload),
    }


def open_public_object(key: str):
    """Buka stream objek publik. Return (stream, content_type, length)."""
    if not SAFE_OBJECT_KEY.match(key or ''):
        raise ObjectNotFound()

    if settings.MINIO_ENABLED:
        from botocore.exceptions import ClientError

        client = _s3_client()
        try:
            obj = client.get_object(Bucket=settings.MINIO_BUCKET, Key=key)
        except ClientError as exc:
            code = exc.response.get('Error', {}).get('Code', '')
            if code in {'NoSuchKey', '404', 'NotFound'}:
                raise ObjectNotFound() from exc
            raise
        content_type = obj.get('ContentType') or WEBP_CONTENT_TYPE
        return obj['Body'], content_type, obj.get('ContentLength')

    path = (Path(settings.MEDIA_ROOT) / key).resolve()
    media_root = Path(settings.MEDIA_ROOT).resolve()
    if media_root not in path.parents and path != media_root:
        raise ObjectNotFound()
    if not path.is_file():
        raise ObjectNotFound()
    suffix = path.suffix.lower()
    content_type = 'image/webp' if suffix == '.webp' else (
        'image/png' if suffix == '.png' else 'image/jpeg'
    )
    return path.open('rb'), content_type, path.stat().st_size
