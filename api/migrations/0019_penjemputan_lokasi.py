from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_fase8_6_device_token_fcm'),
    ]

    operations = [
        migrations.AddField(
            model_name='penjemputan',
            name='latitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                help_text='Latitude lokasi jemput (opsional, bukan live tracking).',
                max_digits=9,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='penjemputan',
            name='longitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                help_text='Longitude lokasi jemput (opsional, bukan live tracking).',
                max_digits=9,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='penjemputan',
            name='catatan_lokasi',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Patokan lokasi (opsional), mis. dekat warung X.',
                max_length=255,
            ),
        ),
    ]
