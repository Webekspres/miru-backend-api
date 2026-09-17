# Audit Temuan T6/T7/T8 — jenis lainnya, jam_buka/jam_tutup, edukasi markdown help
# Renumbered from T6 0019_audit_t6_t7_t8 → 0022 (after 0021_t2_phone_otp_verified)

import datetime

from django.db import migrations, models


def seed_jam_operasional(apps, schema_editor):
    PengaturanInstitusi = apps.get_model('api', 'PengaturanInstitusi')
    for row in PengaturanInstitusi.objects.all():
        changed = False
        if row.jam_buka is None:
            row.jam_buka = datetime.time(8, 0)
            changed = True
        if row.jam_tutup is None:
            row.jam_tutup = datetime.time(17, 0)
            changed = True
        if changed:
            if row.jam_buka and row.jam_tutup:
                row.jam_operasional = (
                    f'{row.jam_buka.strftime("%H.%M")}–'
                    f'{row.jam_tutup.strftime("%H.%M")} WIT'
                )
            row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_t2_phone_otp_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pengaduan',
            name='jenis_pengaduan',
            field=models.CharField(
                choices=[
                    ('saldo_belum_masuk', 'Saldo Belum Masuk'),
                    ('penjemputan_terlambat', 'Penjemputan Terlambat'),
                    ('berat_tidak_sesuai', 'Berat Tidak Sesuai'),
                    ('harga_tidak_sesuai', 'Harga Tidak Sesuai'),
                    ('petugas_tidak_datang', 'Petugas Tidak Datang'),
                    ('kesalahan_data', 'Kesalahan Data'),
                    ('bukti_tidak_muncul', 'Bukti Tidak Muncul'),
                    ('lainnya', 'Lainnya'),
                ],
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='pengaturaninstitusi',
            name='jam_buka',
            field=models.TimeField(
                blank=True,
                help_text='Jam buka layanan (WIT)',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='pengaturaninstitusi',
            name='jam_tutup',
            field=models.TimeField(
                blank=True,
                help_text='Jam tutup layanan (WIT)',
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='pengaturaninstitusi',
            name='jam_operasional',
            field=models.CharField(
                blank=True,
                default='',
                help_text=(
                    'Deprecated: gunakan jam_buka/jam_tutup. '
                    'Disinkron otomatis untuk client lama.'
                ),
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name='pengaturaninstitusi',
            name='logo_url',
            field=models.URLField(
                blank=True,
                help_text=(
                    'Deprecated: logo fiks pakai ikon app; '
                    'field diabaikan pada write.'
                ),
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='kontenedukasi',
            name='isi',
            field=models.TextField(
                help_text=(
                    'Markdown mentah. Subset diizinkan: heading (#–###), '
                    'bold/italic (* * / ** **), unordered/ordered list, '
                    'link [teks](url), inline code, fenced code block. '
                    'Tidak perlu HTML; server menyimpan teks mentah tanpa '
                    'sanitizer HTML berat.'
                ),
            ),
        ),
        migrations.RunPython(seed_jam_operasional, migrations.RunPython.noop),
    ]
