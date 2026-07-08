from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_pengaduan_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('nasabah', 'Nasabah'),
                    ('petugas', 'Petugas'),
                    ('admin', 'Admin Aplikasi'),
                    ('koordinator', 'Koordinator'),
                    ('pemerintah', 'Pemerintah Distrik'),
                ],
                default='nasabah',
                max_length=20,
            ),
        ),
    ]
