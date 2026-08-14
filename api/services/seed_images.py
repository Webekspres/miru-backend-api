"""Gambar demo untuk seed — generate PNG, upload via object_storage (jadi WebP)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageDraw, ImageFont

from api.services.object_storage import save_public_image

AVATAR_PALETTE = [
    (16, 122, 84),
    (30, 90, 140),
    (180, 90, 40),
    (120, 50, 130),
    (40, 110, 110),
    (150, 60, 70),
    (70, 90, 40),
    (50, 70, 120),
]

COVER_PALETTE = [
    (18, 92, 68),
    (28, 78, 118),
    (120, 72, 32),
    (72, 52, 112),
    (36, 96, 96),
    (128, 56, 64),
    (48, 88, 44),
]


def _font(size: int) -> ImageFont.ImageFont:
    for path in (
        Path(r'C:\Windows\Fonts\segoeui.ttf'),
        Path(r'C:\Windows\Fonts\arial.ttf'),
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
    ):
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _initials(nama: str) -> str:
    parts = [p for p in (nama or '').split() if p]
    if len(parts) >= 2:
        return f'{parts[0][0]}{parts[1][0]}'.upper()
    if parts:
        return parts[0][:2].upper()
    return '?'


def _color_index(seed: str, size: int) -> int:
    return sum(ord(ch) for ch in seed) % size


def _to_upload(image: Image.Image, name: str) -> SimpleUploadedFile:
    buf = BytesIO()
    image.save(buf, format='PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


_AVATAR_KEYS: dict[str, str] = {}


def reset_seed_image_cache() -> None:
    _AVATAR_KEYS.clear()


def upload_avatar(nama: str, *, seed: str = '') -> str:
    text = _initials(nama)
    color_i = _color_index(seed or nama, len(AVATAR_PALETTE))
    cache_key = f'{text}:{color_i}'
    cached = _AVATAR_KEYS.get(cache_key)
    if cached:
        return cached

    color = AVATAR_PALETTE[color_i]
    image = Image.new('RGB', (512, 512), color)
    draw = ImageDraw.Draw(image)
    font = _font(180)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((512 - tw) / 2 - bbox[0], (512 - th) / 2 - bbox[1]),
        text,
        fill=(255, 255, 255),
        font=font,
    )
    key = save_public_image(_to_upload(image, 'avatar.png'), purpose='avatar')['key']
    _AVATAR_KEYS[cache_key] = key
    return key


def upload_article_cover(judul: str, urutan: int = 0) -> str:
    bg = COVER_PALETTE[urutan % len(COVER_PALETTE)]
    image = Image.new('RGB', (1600, 900), bg)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1600, 18), fill=(255, 255, 255))
    draw.rectangle((0, 720, 1600, 900), fill=(12, 28, 22))
    draw.ellipse((1180, -80, 1780, 520), fill=tuple(min(255, c + 28) for c in bg))
    font = _font(54)
    title = judul if len(judul) <= 42 else f'{judul[:40]}…'
    draw.text((80, 760), title, fill=(255, 255, 255), font=font)
    draw.text((80, 830), 'MIRU Bank Sampah', fill=(180, 220, 200), font=_font(28))
    return save_public_image(_to_upload(image, 'cover.png'), purpose='edukasi')['key']
