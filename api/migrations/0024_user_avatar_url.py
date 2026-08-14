from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_kontenedukasi_gambar_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar_url',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Key objek MinIO (avatar/...) atau URL foto profil.',
                max_length=500,
            ),
        ),
    ]
