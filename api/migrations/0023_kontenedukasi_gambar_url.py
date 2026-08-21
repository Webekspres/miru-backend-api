from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_audit_t6_t7_t8'),
    ]

    operations = [
        migrations.AddField(
            model_name='kontenedukasi',
            name='gambar_url',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Key objek MinIO (edukasi/...) atau URL gambar eksternal.',
                max_length=500,
            ),
        ),
    ]
