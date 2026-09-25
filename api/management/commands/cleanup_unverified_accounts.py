"""Hapus pendaftaran nasabah yang tidak pernah memverifikasi email.

Akun seperti ini tidak pernah aktif (tidak ada transaksi) — biasanya
pendaftaran bot atau pendaftaran yang ditinggalkan. Jalankan terjadwal,
misalnya harian via cron:  python manage.py cleanup_unverified_accounts
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import User


class Command(BaseCommand):
    help = 'Hapus nasabah belum aktif yang tidak memverifikasi email dalam N jam.'

    def add_arguments(self, parser):
        parser.add_argument('--hours', type=int, default=24)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=options['hours'])
        qs = User.objects.filter(
            role='nasabah',
            is_active=False,
            last_login__isnull=True,
            email_verified=False,
            date_joined__lt=cutoff,
        )
        count = qs.count()
        if options['dry_run']:
            self.stdout.write(f'{count} akun akan dihapus (dry run).')
            return
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f'{count} akun belum terverifikasi dihapus.'))
