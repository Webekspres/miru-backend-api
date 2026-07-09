from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('nasabah', 'Nasabah'),
        ('petugas', 'Petugas'),
        ('admin', 'Admin Aplikasi'),
        ('koordinator', 'Koordinator'),
        ('pemerintah', 'Pemerintah Distrik'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='nasabah')
    nama_lengkap = models.CharField(max_length=255)
    nik = models.CharField(max_length=16, blank=True)
    no_hp = models.CharField(max_length=15, blank=True)
    alamat = models.TextField(blank=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    poin = models.IntegerField(default=0)
    setuju_kebijakan_data = models.BooleanField(default=False)
    tanggal_persetujuan_kebijakan = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['role']),
        ]

class KategoriSampah(models.Model):
    nama = models.CharField(max_length=100)
    harga_beli_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    stok_terkini_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = 'Kategori Sampah'
        indexes = [
            models.Index(fields=['nama']),
        ]

class RiwayatHarga(models.Model):
    kategori = models.ForeignKey(
        KategoriSampah, on_delete=models.CASCADE, related_name='riwayat_harga',
    )
    harga_lama = models.DecimalField(max_digits=10, decimal_places=2)
    harga_baru = models.DecimalField(max_digits=10, decimal_places=2)
    tanggal_berlaku = models.DateTimeField(auto_now_add=True)
    diubah_oleh = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='riwayat_harga_diubah',
    )

    class Meta:
        ordering = ['-tanggal_berlaku']

    def __str__(self):
        return f'{self.kategori.nama}: {self.harga_lama} → {self.harga_baru}'

class TransaksiSetoran(models.Model):
    nasabah = models.ForeignKey(User, on_delete=models.CASCADE, related_name='setoran_nasabah')
    petugas = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='setoran_petugas')
    tanggal = models.DateTimeField(auto_now_add=True)
    total_nilai = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='selesai') # SOP says direct setor is verified and added immediately

    class Meta:
        verbose_name_plural = 'Transaksi Setoran'
        indexes = [
            models.Index(fields=['tanggal']),
            models.Index(fields=['nasabah']),
        ]

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
        ('dalam_perjalanan', 'Dalam Perjalanan'),
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

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['nasabah']),
            models.Index(fields=['petugas']),
        ]

class PenarikanSaldo(models.Model):
    STATUS_CHOICES = (
        ('menunggu', 'Menunggu'),
        ('selesai', 'Selesai'),
        ('ditolak', 'Ditolak'),
    )
    nasabah = models.ForeignKey(User, on_delete=models.CASCADE)
    nominal = models.DecimalField(max_digits=12, decimal_places=2)
    metode = models.CharField(max_length=50)
    nama_bank = models.CharField(max_length=100, blank=True, default='')
    no_rekening = models.CharField(max_length=30, blank=True, default='')
    nama_pemilik_rekening = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')
    tanggal = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Penarikan Saldo'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['nasabah']),
            models.Index(fields=['tanggal']),
        ]

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

class AuditLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=20)  # create, update, delete
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=36)  # PK as string (supports UUID in future)
    changes = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_name']),
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f'{self.action} {self.model_name}#{self.object_id} by {self.user_id}'


DEFAULT_INSTITUTION = {
    'nama_institusi': 'Bank Sampah MIRU - Distrik Mimika Baru',
    'alamat': 'Jl. Cendrawasih Poros SP.II, Timika, Papua Tengah 99910',
    'kontak': '0821 977 3693',
    'email': 'distrikmiru@mimikakab.go.id',
    'jam_operasional': 'Senin–Sabtu, 08.00–17.00 WIT',
    'pengumuman': 'Selamat datang di MIRU Bank Sampah!',
}


class PengaturanInstitusi(models.Model):
    """Singleton — profil institusi bank sampah (pk selalu 1)."""

    nama_institusi = models.CharField(max_length=255)
    alamat = models.TextField(blank=True, default='')
    kontak = models.CharField(max_length=50, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    logo_url = models.URLField(blank=True, null=True)
    jam_operasional = models.CharField(max_length=255, blank=True, default='')
    pengumuman = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Pengaturan Institusi'
        verbose_name_plural = 'Pengaturan Institusi'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults=DEFAULT_INSTITUTION)
        return obj

    def __str__(self):
        return self.nama_institusi


class Pengumuman(models.Model):
    judul = models.CharField(max_length=200)
    isi = models.TextField()
    aktif = models.BooleanField(default=True)
    tanggal = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tanggal']
        verbose_name_plural = 'Pengumuman'

    def __str__(self):
        return self.judul


class Pengaduan(models.Model):
    JENIS_CHOICES = (
        ('saldo_belum_masuk', 'Saldo Belum Masuk'),
        ('penjemputan_terlambat', 'Penjemputan Terlambat'),
        ('berat_tidak_sesuai', 'Berat Tidak Sesuai'),
        ('harga_tidak_sesuai', 'Harga Tidak Sesuai'),
        ('petugas_tidak_datang', 'Petugas Tidak Datang'),
        ('kesalahan_data', 'Kesalahan Data'),
        ('bukti_tidak_muncul', 'Bukti Tidak Muncul'),
    )
    STATUS_CHOICES = (('terbuka', 'Terbuka'), ('ditutup', 'Ditutup'))
    nasabah = models.ForeignKey(User, on_delete=models.CASCADE)
    jenis_pengaduan = models.CharField(max_length=30, choices=JENIS_CHOICES)
    keluhan = models.TextField()
    tindak_lanjut = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='terbuka')
    tanggal = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Pengaduan'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['nasabah']),
        ]
