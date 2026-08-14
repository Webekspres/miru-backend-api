from django.db import migrations, models


def wipe_identity_pii(apps, schema_editor):
    User = apps.get_model('api', 'User')
    PenarikanSaldo = apps.get_model('api', 'PenarikanSaldo')

    User.objects.all().update(nik='', nik_encrypted='')

    for user in User.objects.exclude(foto_ktp='').exclude(foto_ktp__isnull=True):
        name = user.foto_ktp.name
        if name and user.foto_ktp.storage.exists(name):
            user.foto_ktp.storage.delete(name)
        user.foto_ktp = None
        user.save(update_fields=['foto_ktp'])

    for row in PenarikanSaldo.objects.exclude(status='menunggu'):
        name = row.lampiran_ktp.name if row.lampiran_ktp else ''
        if name and row.lampiran_ktp.storage.exists(name):
            row.lampiran_ktp.storage.delete(name)
        row.lampiran_ktp = None
        row.save(update_fields=['lampiran_ktp'])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_institusi_tentang_kebijakan'),
    ]

    operations = [
        migrations.RunPython(wipe_identity_pii, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='user',
            name='foto_ktp',
        ),
        migrations.RemoveField(
            model_name='user',
            name='nik',
        ),
        migrations.RemoveField(
            model_name='user',
            name='nik_encrypted',
        ),
        migrations.AddField(
            model_name='penarikansaldo',
            name='ktp_diverifikasi',
            field=models.BooleanField(
                default=False,
                help_text='True setelah lampiran KTP dilihat dan penarikan disetujui/ditolak (file sudah dihapus).',
            ),
        ),
        migrations.AlterField(
            model_name='penarikansaldo',
            name='lampiran_ktp',
            field=models.FileField(
                blank=True,
                help_text='Lampiran KTP sementara untuk penarikan ≥ Rp1.000.000; dihapus setelah diproses.',
                null=True,
                upload_to='lampiran_ktp/',
            ),
        ),
    ]
