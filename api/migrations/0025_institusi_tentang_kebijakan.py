from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_user_avatar_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='pengaturaninstitusi',
            name='tentang',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Markdown halaman Tentang MIRU (mobile & web).',
            ),
        ),
        migrations.AddField(
            model_name='pengaturaninstitusi',
            name='kebijakan',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Markdown kebijakan data pribadi (mobile & web).',
            ),
        ),
    ]
