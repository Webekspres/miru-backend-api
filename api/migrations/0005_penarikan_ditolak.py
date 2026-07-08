from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_user_role_pemerintah'),
    ]

    operations = [
        migrations.AlterField(
            model_name='penarikansaldo',
            name='status',
            field=models.CharField(
                choices=[
                    ('menunggu', 'Menunggu'),
                    ('selesai', 'Selesai'),
                    ('ditolak', 'Ditolak'),
                ],
                default='menunggu',
                max_length=20,
            ),
        ),
    ]
