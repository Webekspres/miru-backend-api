from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_penjemputan_dalam_perjalanan'),
    ]

    operations = [
        migrations.AddField(
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
                ],
                default='saldo_belum_masuk',
                max_length=30,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pengaduan',
            name='tindak_lanjut',
            field=models.TextField(blank=True, default=''),
        ),
    ]
