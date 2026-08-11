from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

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
    nik_encrypted = models.TextField(
        blank=True, default='',
        help_text='NIK terenkripsi at-rest (Fase 8.4)',
    )
    no_hp = models.CharField(max_length=15, blank=True)
    phone_verified = models.BooleanField(
        default=False,
        help_text='True jika nomor HP sudah diverifikasi OTP WhatsApp (T2/T10)',
    )
    alamat = models.TextField(blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text='Koordinat lat profil (opsional, maps)',
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text='Koordinat lng profil (opsional, maps)',
    )
    patokan = models.CharField(
        max_length=255, blank=True, default='',
        help_text='Patokan lokasi / keterangan maps (opsional)',
    )
    foto_ktp = models.FileField(
        upload_to='ktp/',
        null=True, blank=True,
        help_text='Foto KTP untuk verifikasi identitas (Fase 8.4)',
    )
    kelurahan = models.ForeignKey(
        'WilayahLayanan', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='penduduk',
        help_text='Kelurahan/kampung domisili (Fase 8.3)',
    )
    rt = models.CharField(max_length=10, blank=True, default='', help_text='RT (opsional)')
    rw = models.CharField(max_length=10, blank=True, default='', help_text='RW (opsional)')
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    poin = models.IntegerField(default=0)
    setuju_kebijakan_data = models.BooleanField(default=False)
    tanggal_persetujuan_kebijakan = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['role']),
        ]

    def get_nik(self) -> str:
        """
        Decrypt and return NIK. Falls back to plaintext `nik` if not encrypted.
        Call this whenever reading NIK for display.
        """
        if self.nik_encrypted:
            from api.services.encryption import decrypt_value
            try:
                return decrypt_value(self.nik_encrypted)
            except Exception:
                pass
        return self.nik

    def encrypt_nik(self, plain_nik: str) -> None:
        """Encrypt plaintext NIK and store in both nik and nik_encrypted fields."""
        from api.services.encryption import encrypt_value
        self.nik = plain_nik
        self.nik_encrypted = encrypt_value(plain_nik)

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
    tanggal_berlaku = models.DateTimeField(
        default=timezone.now,
        help_text='Harga mulai berlaku pada tanggal ini (min H+3 dari penetapan)',
    )
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
    # Koordinat opsional untuk peta di mobile — bukan GPS live tracking.
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text='Latitude lokasi jemput (opsional, bukan live tracking).',
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text='Longitude lokasi jemput (opsional, bukan live tracking).',
    )
    catatan_lokasi = models.CharField(
        max_length=255, blank=True, default='',
        help_text='Patokan lokasi (opsional), mis. dekat warung X.',
    )
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
    lampiran_ktp = models.FileField(
        upload_to='lampiran_ktp/',
        null=True, blank=True,
        help_text='Lampiran KTP untuk penarikan besar ≥ Rp1.000.000 (Fase 8.4)',
    )
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
    STATUS_CHOICES = (
        ('menunggu', 'Menunggu'),
        ('selesai', 'Selesai'),
        ('ditolak', 'Ditolak'),
        ('dibatalkan', 'Dibatalkan'),
    )
    nasabah = models.ForeignKey(User, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.RESTRICT)
    # Snapshot biaya poin saat pengajuan — approve memakai nilai ini, bukan harga katalog terbaru.
    poin_dibutuhkan = models.PositiveIntegerField(
        help_text='Snapshot poin saat pengajuan; tidak berubah jika harga katalog berubah.',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')
    tanggal = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Qty tetap 1 per baris (multi-qty deferred). Snapshot dari katalog jika belum diisi.
        if self.reward_id and not self.poin_dibutuhkan:
            reward_poin = (
                Reward.objects.filter(pk=self.reward_id)
                .values_list('poin_dibutuhkan', flat=True)
                .first()
            )
            if reward_poin:
                self.poin_dibutuhkan = reward_poin
        super().save(*args, **kwargs)

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


from datetime import time as _time

DEFAULT_INSTITUTION = {
    'nama_institusi': 'Bank Sampah MIRU - Distrik Mimika Baru',
    'alamat': 'Jl. Cendrawasih Poros SP.II, Timika, Papua Tengah 99910',
    'kontak': '0821 977 3693',
    'email': 'distrikmiru@mimikakab.go.id',
    'jam_operasional': 'Senin–Sabtu, 08.00–17.00 WIT',
    'jam_buka': _time(8, 0),
    'jam_tutup': _time(17, 0),
    'pengumuman': 'Selamat datang di MIRU Bank Sampah!',
}


class PengaturanInstitusi(models.Model):
    """Singleton — profil institusi bank sampah (pk selalu 1)."""

    nama_institusi = models.CharField(max_length=255)
    alamat = models.TextField(blank=True, default='')
    kontak = models.CharField(max_length=50, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    logo_url = models.URLField(
        blank=True, null=True,
        help_text='Deprecated: logo fiks pakai ikon app; field diabaikan pada write.',
    )
    jam_operasional = models.CharField(
        max_length=255, blank=True, default='',
        help_text='Deprecated: gunakan jam_buka/jam_tutup. Disinkron otomatis untuk client lama.',
    )
    jam_buka = models.TimeField(
        null=True, blank=True,
        help_text='Jam buka layanan (WIT)',
    )
    jam_tutup = models.TimeField(
        null=True, blank=True,
        help_text='Jam tutup layanan (WIT)',
    )
    pengumuman = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Pengaturan Institusi'
        verbose_name_plural = 'Pengaturan Institusi'

    def save(self, *args, **kwargs):
        self.pk = 1
        if self.jam_buka and self.jam_tutup:
            self.jam_operasional = (
                f'{self.jam_buka.strftime("%H.%M")}–'
                f'{self.jam_tutup.strftime("%H.%M")} WIT'
            )
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


class Notifikasi(models.Model):
    """In-app notification untuk user nasabah."""

    KATEGORI_CHOICES = (
        ('setoran', 'Setoran'),
        ('penjemputan', 'Penjemputan'),
        ('penarikan', 'Penarikan Saldo'),
        ('penukaran', 'Penukaran Poin'),
        ('pengaduan', 'Pengaduan'),
        ('pengumuman', 'Pengumuman'),
        ('harga', 'Perubahan Harga'),
        ('sistem', 'Sistem'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifikasi',
        help_text='Penerima notifikasi',
    )
    judul = models.CharField(max_length=200)
    deskripsi = models.TextField()
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='sistem')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notifikasi'
        verbose_name_plural = 'Notifikasi'
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'[{self.get_kategori_display()}] {self.judul} — {self.user.username}'


class DeviceToken(models.Model):
    """FCM device token milik user (Fase 8.6)."""

    PLATFORM_CHOICES = (
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='device_tokens',
    )
    token = models.CharField(max_length=512, unique=True)
    platform = models.CharField(
        max_length=20, choices=PLATFORM_CHOICES, default='android',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Device Token'
        verbose_name_plural = 'Device Tokens'
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f'{self.user_id}:{self.platform}:{self.token[:12]}…'


class PasswordResetToken(models.Model):
    """
    Token reset password dengan masa berlaku 1 jam (Fase 8.4).
    Diterbitkan setelah OTP WhatsApp diverifikasi (T2).
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reset_tokens',
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Token Reset Password'
        verbose_name_plural = 'Token Reset Password'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.created_at.isoformat()}'

    @property
    def is_expired(self) -> bool:
        from datetime import timedelta
        from django.utils import timezone
        return timezone.now() > self.created_at + timedelta(hours=1)


class PhoneOTP(models.Model):
    """OTP WhatsApp untuk reset password / verifikasi HP (T2). Kode disimpan sebagai hash."""

    PURPOSE_PASSWORD_RESET = 'password_reset'
    PURPOSE_PHONE_VERIFY = 'phone_verify'
    PURPOSE_REGISTRATION = 'registration'
    PURPOSE_CHOICES = (
        (PURPOSE_PASSWORD_RESET, 'Reset Password'),
        (PURPOSE_PHONE_VERIFY, 'Verifikasi HP'),
        (PURPOSE_REGISTRATION, 'Registrasi'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='phone_otps',
    )
    purpose = models.CharField(max_length=32, choices=PURPOSE_CHOICES)
    phone = models.CharField(max_length=15)
    code_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'OTP Telepon'
        verbose_name_plural = 'OTP Telepon'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'purpose', 'is_used']),
        ]

    def __str__(self):
        return f'{self.user_id}:{self.purpose}:{self.created_at.isoformat()}'

    @property
    def is_expired(self) -> bool:
        from django.utils import timezone
        return timezone.now() >= self.expires_at


class PoinTransaksi(models.Model):
    """
    Riwayat perolehan poin dengan masa berlaku 1 tahun (Fase 8.5).
    
    Setiap kali nasabah mendapat poin (dari setoran), dibuat record di sini.
    Poin hangus otomatis jika `tanggal_kedaluwarsa` terlewat.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='poin_transaksi',
        help_text='Nasabah pemilik poin',
    )
    SUMBER_CHOICES = (
        ('setoran', 'Setoran'),
        ('koreksi', 'Koreksi'),
    )
    sumber = models.CharField(
        max_length=20, choices=SUMBER_CHOICES, default='setoran',
    )
    setoran = models.ForeignKey(
        'TransaksiSetoran', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='poin_transaksi',
        help_text='Transaksi setoran asal (jika dari setoran)',
    )
    jumlah = models.IntegerField(help_text='Jumlah poin (positif = diperoleh, negatif = hangus/dipakai)')
    sisa = models.IntegerField(help_text='Sisa poin yang belum hangus/dipakai')
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)
    tanggal_kedaluwarsa = models.DateTimeField(
        help_text='Poin hangus jika melewati tanggal ini (1 tahun dari perolehan)',
    )
    is_expired = models.BooleanField(
        default=False,
        help_text='True jika poin sudah hangus oleh scheduled task',
    )

    class Meta:
        verbose_name = 'Riwayat Poin'
        verbose_name_plural = 'Riwayat Poin'
        ordering = ['tanggal_dibuat']
        indexes = [
            models.Index(fields=['user', 'is_expired']),
            models.Index(fields=['tanggal_kedaluwarsa']),
        ]

    def __str__(self):
        return f'{self.user.username}: {self.jumlah} poin ({self.sumber})'


class WilayahLayanan(models.Model):
    """Referensi wilayah layanan — kelurahan/kampung di Distrik Mimika Baru."""

    kelurahan = models.CharField(max_length=100, db_index=True)
    rt = models.CharField(max_length=10, blank=True, default='', help_text='RT (opsional)')
    rw = models.CharField(max_length=10, blank=True, default='', help_text='RW (opsional)')
    aktif = models.BooleanField(default=True, help_text='Wilayah yang masih dilayani')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Wilayah Layanan'
        verbose_name_plural = 'Wilayah Layanan'
        ordering = ['kelurahan', 'rt', 'rw']
        indexes = [
            models.Index(fields=['kelurahan']),
            models.Index(fields=['aktif']),
        ]

    def __str__(self):
        parts = [self.kelurahan]
        if self.rt:
            parts.append(f'RT {self.rt}')
        if self.rw:
            parts.append(f'RW {self.rw}')
        return ' '.join(parts)


# Subset Markdown yang diizinkan untuk KontenEdukasi.isi (simpan mentah; render di client).
EDUKASI_MARKDOWN_SUBSET = (
    'heading (#–###), bold/italic (* * / ** **), unordered/ordered list, '
    'link [teks](url), inline code, fenced code block. '
    'Tidak perlu HTML; server menyimpan teks mentah tanpa sanitizer HTML berat.'
)


class KontenEdukasi(models.Model):
    """Konten edukasi sampah — artikel/panduan untuk nasabah (Modul 4)."""

    judul = models.CharField(max_length=200)
    isi = models.TextField(
        help_text=f'Markdown mentah. Subset diizinkan: {EDUKASI_MARKDOWN_SUBSET}',
    )
    kategori_terkait = models.ForeignKey(
        'KategoriSampah', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='konten_edukasi',
        help_text='Kategori sampah terkait (opsional)',
    )
    aktif = models.BooleanField(default=True)
    urutan = models.IntegerField(default=0, help_text='Urutan tampil (ascending)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Konten Edukasi'
        verbose_name_plural = 'Konten Edukasi'
        ordering = ['urutan', 'created_at']

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
        ('lainnya', 'Lainnya'),
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
