"""
Management command: expire_poin

Menghanguskan poin nasabah yang sudah melebihi masa berlaku 1 tahun.

Alur:
1. Cari semua PoinTransaksi dengan is_expired=False dan tanggal_kedaluwarsa <= now
2. Hitung total poin hangus per nasabah
3. Kurangi User.poin secara atomik
4. Catat ke AuditLog
5. Buat Notifikasi untuk nasabah yang poinnya hangus

Cara pakai:
    python manage.py expire_poin              # dry-run (preview)
    python manage.py expire_poin --commit     # benar-benar hanguskan
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from api.models import AuditLog, Notifikasi, PoinTransaksi, User


class Command(BaseCommand):
    help = 'Hanguskan poin nasabah yang sudah lewat masa berlaku 1 tahun.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            action='store_true',
            help='Benar-benar hanguskan poin (tanpa flag ini hanya dry-run).',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        commit = options['commit']

        # Cari PoinTransaksi yang sudah lewat kedaluwarsa
        expired_qs = PoinTransaksi.objects.filter(
            is_expired=False,
            sisa__gt=0,
            tanggal_kedaluwarsa__lte=now,
        ).select_related('user').order_by('user_id', 'tanggal_dibuat')

        total_expired = expired_qs.count()
        if total_expired == 0:
            self.stdout.write(self.style.SUCCESS('Tidak ada poin yang perlu dihanguskan.'))
            return

        # Group by user
        user_totals = {}  # user_id -> {user, total_sisa, records}
        for pt in expired_qs:
            if pt.user_id not in user_totals:
                user_totals[pt.user_id] = {
                    'user': pt.user,
                    'total_sisa': 0,
                    'records': [],
                }
            user_totals[pt.user_id]['total_sisa'] += pt.sisa
            user_totals[pt.user_id]['records'].append(pt)

        if not commit:
            # Dry-run: tampilkan preview
            self.stdout.write(self.style.WARNING(
                f'🔍 DRY-RUN: {total_expired} record poin akan dihanguskan '
                f'pada {len(user_totals)} nasabah.\n'
                'Jalankan dengan --commit untuk benar-benar menghanguskan.\n'
            ))
            for uid, info in sorted(user_totals.items()):
                self.stdout.write(
                    f'  • {info["user"].username}: '
                    f'{info["total_sisa"]} poin '
                    f'({len(info["records"])} record)'
                )
            return

        # Commit: benar-benar hanguskan
        self.stdout.write('⏳ Menghanguskan poin...')

        affected_count = 0
        for uid, info in sorted(user_totals.items()):
            total_sisa = info['total_sisa']
            user = info['user']

            with transaction.atomic():
                # Lock user row
                locked = User.objects.select_for_update().get(pk=uid)
                locked.poin -= total_sisa
                if locked.poin < 0:
                    locked.poin = 0  # Safety: jangan sampai negatif
                locked.save(update_fields=['poin'])

                # Mark PoinTransaksi records as expired
                pt_ids = [pt.pk for pt in info['records']]
                PoinTransaksi.objects.filter(pk__in=pt_ids).update(is_expired=True)

                # Create negative PoinTransaksi records
                PoinTransaksi.objects.create(
                    user=user,
                    sumber='koreksi',
                    setoran=None,
                    jumlah=-total_sisa,
                    sisa=0,
                    tanggal_kedaluwarsa=now,
                    is_expired=True,
                )

                # AuditLog
                AuditLog.objects.create(
                    user=None,  # System action
                    action='update',
                    model_name='User',
                    object_id=str(user.pk),
                    changes={
                        'poin': {
                            'old': locked.poin + total_sisa,
                            'new': locked.poin,
                        },
                        'reason': 'poin_expired_1_year',
                    },
                    ip_address=None,
                )

                # Notifikasi
                Notifikasi.objects.create(
                    user=user,
                    judul='Poin Telah Hangus',
                    deskripsi=(
                        f'Poin Anda sebanyak {total_sisa} telah hangus '
                        f'karena sudah melebihi masa berlaku 1 tahun. '
                        f'Ayo setor sampah untuk mengumpulkan poin baru!'
                    ),
                    kategori='sistem',
                )

                affected_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'✅ {total_expired} record poin dihanguskan pada '
            f'{affected_count} nasabah.\n'
            f'   Notifikasi dan AuditLog telah dibuat.'
        ))
