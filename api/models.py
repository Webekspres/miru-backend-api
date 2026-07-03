from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('nasabah', 'Nasabah'),
        ('petugas', 'Petugas'),
        ('admin', 'Admin Aplikasi'),
        ('koordinator', 'Koordinator'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='nasabah')
    nik = models.CharField(max_length=16, blank=True)
    no_hp = models.CharField(max_length=15, blank=True)
    alamat = models.TextField(blank=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    poin = models.IntegerField(default=0)

class KategoriSampah(models.Model):
    nama = models.CharField(max_length=100)
    harga_beli_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    stok_terkini_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class TransaksiSetoran(models.Model):
    nasabah = models.ForeignKey(User, on_delete=models.CASCADE, related_name='setoran_nasabah')
    petugas = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='setoran_petugas')
    tanggal = models.DateTimeField(auto_now_add=True)
    total_nilai = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='selesai') # SOP says direct setor is verified and added immediately

class DetailSetoran(models.Model):
    transaksi = models.ForeignKey(TransaksiSetoran, on_delete=models.CASCADE, related_name='details')
    kategori = models.ForeignKey(KategoriSampah, on_delete=models.RESTRICT)
    berat_kg = models.DecimalField(max_digits=8, decimal_places=2)
    harga_saat_itu = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

class Penjemputan(models.Model):
    STATUS_CHOICES = (
        ('menunggu', 'Menunggu'),
        ('disetujui', 'Disetujui'),
        ('dijadwalkan', 'Dijadwalkan'),
        ('dijemput', 'Dijemput'),
        ('selesai', 'Selesai'),
        ('ditolak', 'Ditolak'),
    )
    nasabah = models.ForeignKey(User, on_delete=models.CASCADE, related_name='penjemputan_nasabah')
    petugas = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='penjemputan_petugas')
    estimasi_berat = models.DecimalField(max_digits=8, decimal_places=2)
    alamat_jemput = models.TextField()
    jadwal = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')

class PenarikanSaldo(models.Model):
    STATUS_CHOICES = (('menunggu', 'Menunggu'), ('selesai', 'Selesai'))
    nasabah = models.ForeignKey(User, on_delete=models.CASCADE)
    nominal = models.DecimalField(max_digits=12, decimal_places=2)
    metode = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')
    tanggal = models.DateTimeField(auto_now_add=True)

class Reward(models.Model):
    nama = models.CharField(max_length=100)
    poin_dibutuhkan = models.IntegerField()
    stok = models.IntegerField()

class PenukaranPoin(models.Model):
    STATUS_CHOICES = (('menunggu', 'Menunggu'), ('selesai', 'Selesai'))
    nasabah = models.ForeignKey(User, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.RESTRICT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')
    tanggal = models.DateTimeField(auto_now_add=True)

class MitraPengepul(models.Model):
    nama = models.CharField(max_length=100)
    kontak = models.CharField(max_length=50)

class PenjualanMitra(models.Model):
    mitra = models.ForeignKey(MitraPengepul, on_delete=models.CASCADE)
    kategori = models.ForeignKey(KategoriSampah, on_delete=models.RESTRICT)
    berat_jual_kg = models.DecimalField(max_digits=8, decimal_places=2)
    harga_jual_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    total_penjualan = models.DecimalField(max_digits=12, decimal_places=2)
    tanggal = models.DateTimeField(auto_now_add=True)

class Pengaduan(models.Model):
    STATUS_CHOICES = (('terbuka', 'Terbuka'), ('ditutup', 'Ditutup'))
    nasabah = models.ForeignKey(User, on_delete=models.CASCADE)
    keluhan = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='terbuka')
    tanggal = models.DateTimeField(auto_now_add=True)
