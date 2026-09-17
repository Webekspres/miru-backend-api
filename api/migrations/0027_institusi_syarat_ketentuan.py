from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_pdp_minimise_identity'),
    ]

    operations = [
        migrations.AddField(
            model_name='pengaturaninstitusi',
            name='syarat_ketentuan',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Markdown syarat & ketentuan (web publik & Play Store).',
            ),
        ),
    ]
