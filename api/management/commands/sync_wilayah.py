"""Perbarui kelurahan/kampung Distrik Mimika Baru dari API wilayah.id.

Data awal sudah ada lewat migrasi; jalankan ini bila ada pemekaran atau
perubahan nama resmi:  python manage.py sync_wilayah --dry-run
Wilayah yang hilang dari data resmi tidak dihapus — nonaktifkan lewat admin.
"""

import json
import urllib.request

from django.core.management.base import BaseCommand, CommandError

from api.models import WilayahLayanan
from api.services.wilayah import DISTRIK, WILAYAH_API_BASE, upsert_kelurahan


class Command(BaseCommand):
    help = 'Sinkronkan kelurahan/kampung Distrik Mimika Baru dari API wilayah.id.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        url = f"{WILAYAH_API_BASE}/villages/{DISTRIK['kode']}.json"
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                data = json.load(resp)['data']
        except Exception as exc:
            raise CommandError(f'Gagal mengambil {url}: {exc}') from exc

        items = [(row['code'], row['name']) for row in data]
        known = set(WilayahLayanan.objects.filter(kode__isnull=False).values_list('kode', flat=True))
        baru = [nama for kode, nama in items if kode not in known]
        self.stdout.write(f"{len(items)} wilayah resmi di Distrik {DISTRIK['nama']}; baru: {baru or '-'}")
        if options['dry_run']:
            return
        upsert_kelurahan(WilayahLayanan, items)
        self.stdout.write(self.style.SUCCESS('Wilayah layanan diperbarui.'))
