# T4 — snapshot poin_dibutuhkan + status ditolak/dibatalkan

from django.db import migrations, models


def backfill_poin_snapshot(apps, schema_editor):
    PenukaranPoin = apps.get_model('api', 'PenukaranPoin')
    for row in PenukaranPoin.objects.select_related('reward').iterator():
        if row.reward_id and row.poin_dibutuhkan == 0:
            row.poin_dibutuhkan = row.reward.poin_dibutuhkan
            row.save(update_fields=['poin_dibutuhkan'])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_penjemputan_lokasi'),
    ]

    operations = [
        migrations.AddField(
            model_name='penukaranpoin',
            name='poin_dibutuhkan',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Snapshot poin saat pengajuan; tidak berubah jika harga katalog berubah.',
            ),
            preserve_default=False,
        ),
        migrations.RunPython(backfill_poin_snapshot, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='penukaranpoin',
            name='status',
            field=models.CharField(
                choices=[
                    ('menunggu', 'Menunggu'),
                    ('selesai', 'Selesai'),
                    ('ditolak', 'Ditolak'),
                    ('dibatalkan', 'Dibatalkan'),
                ],
                default='menunggu',
                max_length=20,
            ),
        ),
    ]
