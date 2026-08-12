"""Kebijakan data pribadi (UU PDP) — konten untuk API publik."""

PRIVACY_POLICY_VERSION = '1.0'
RETENTION_YEARS = 5

PRIVACY_POLICY = {
    'versi': PRIVACY_POLICY_VERSION,
    'judul': 'Kebijakan Data Pribadi MIRU Bank Sampah',
    'institusi': 'Bank Sampah MIRU — Distrik Mimika Baru',
    'dasar_hukum': 'Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi (UU PDP)',
    'ringkasan': (
        'MIRU Bank Sampah mengumpulkan data pribadi nasabah dan petugas '
        'untuk operasional program bank sampah. Data diproses secara terbatas, '
        'disimpan dengan aman, dan dihapus sesuai kebijakan retensi setelah '
        'masa penyimpanan berakhir.'
    ),
    'data_yang_disimpan': [
        {
            'kategori': 'Data identitas nasabah',
            'field': ['username', 'nama_lengkap', 'nik', 'no_hp', 'alamat'],
            'tujuan': 'Registrasi, identifikasi saat setoran, dan komunikasi layanan',
        },
        {
            'kategori': 'Data transaksi',
            'field': [
                'setoran', 'penjemputan', 'penarikan saldo', 'penukaran poin',
                'pengaduan',
            ],
            'tujuan': 'Pencatatan operasional bank sampah dan bukti digital',
        },
        {
            'kategori': 'Data keuangan program',
            'field': ['saldo', 'poin'],
            'tujuan': 'Perhitungan hak nasabah atas setoran dan reward',
        },
        {
            'kategori': 'Data audit',
            'field': ['audit log', 'riwayat harga', 'persetujuan kebijakan'],
            'tujuan': 'Transparansi, akuntabilitas, dan kepatuhan regulasi',
        },
    ],
    'retensi': {
        'masa_tahun': RETENTION_YEARS,
        'keterangan': (
            'Data transaksi dan arsip digital disimpan minimal 5 tahun '
            'sesuai ketentuan tata kelola arsip OPD dan SOP bank sampah. '
            'Setelah masa retensi, data dapat dianonimkan atau dihapus '
            'sesuai keputusan pengelola.'
        ),
    },
    'hak_pengguna': [
        'Mengakses dan memperbarui profil melalui aplikasi',
        'Mengajukan pengaduan terkait data atau layanan',
        'Meminta penjelasan penggunaan data kepada admin program',
    ],
    'persetujuan_registrasi': {
        'field': 'setuju_kebijakan_data',
        'wajib': True,
        'keterangan': (
            'Nasabah wajib menyetujui kebijakan ini saat registrasi. '
            'Waktu persetujuan dicatat di sistem.'
        ),
    },
    'keamanan_data_sensitif': {
        'nik': {
            'status_saat_ini': 'tersimpan_terenkripsi',
            'opsional': True,
            'validasi_dukcapil': False,
            'metode_enkripsi': 'AES-256 (Fernet) — key diturunkan dari SECRET_KEY',
            'implementasi': (
                'Field-level encryption untuk NIK telah diimplementasikan (Fase 8.4). '
                'NIK dienkripsi at-rest menggunakan Fernet (AES-256 dalam mode CBC) '
                'dengan key yang diturunkan dari SECRET_KEY aplikasi. '
                'Dekripsi hanya terjadi saat data ditampilkan di API response.'
            ),
        },
    },
}


DEFAULT_KEBIJAKAN_MD = """# Kebijakan Perlindungan Data Pribadi

**MIRU Bank Sampah** — Distrik Mimika Baru

Berlaku sesuai Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi (UU PDP).

## 1. Pendahuluan

MIRU Bank Sampah berkomitmen melindungi data pribadi nasabah dan petugas. Kebijakan ini menjelaskan bagaimana data dikumpulkan, digunakan, disimpan, dan dilindungi.

## 2. Data yang Dikumpulkan

- Nama lengkap, nomor HP, alamat, username
- NIK (opsional, tersimpan terenkripsi)
- Riwayat transaksi (setoran, penarikan, penukaran poin)
- Foto profil (jika diunggah)

## 3. Tujuan Penggunaan

- Membuat dan mengelola akun
- Memproses setoran, penarikan, dan penukaran poin
- Menghubungi terkait jadwal penjemputan
- Pelaporan kepada pemerintah daerah

## 4. Penyimpanan dan Keamanan

Data disimpan di server yang aman. NIK dienkripsi at-rest. Data tidak dijual kepada pihak ketiga.

## 5. Hak Anda

- Mengakses dan memperbaiki data melalui aplikasi
- Mengajukan pengaduan terkait data atau layanan
- Meminta penjelasan penggunaan data kepada admin program

## 6. Masa Retensi

Data transaksi disimpan minimal 5 tahun sesuai tata kelola arsip. Setelah masa retensi, data dapat dianonimkan atau dihapus.

## 7. Kontak

Hubungi admin MIRU Bank Sampah melalui aplikasi atau kantor Distrik Mimika Baru.
"""

DEFAULT_TENTANG_MD = """# Tentang MIRU

MIRU (Mimika Recycle Unit) adalah aplikasi bank sampah resmi Distrik Mimika Baru, Kabupaten Mimika, Papua Tengah.

> Sampah Bernilai, Lingkungan Bersih, Warga Sejahtera

## Layanan utama

- **Setoran sampah terpilah** — plastik, kertas, logam, dan minyak jelantah
- **Penjemputan** — jadwal jemput oleh petugas bank sampah
- **Saldo & poin** — hasil setoran dapat ditarik atau ditukar reward
- **Pengaduan** — laporkan kendala layanan melalui aplikasi

## Teknologi

Dikembangkan untuk masyarakat Distrik Mimika Baru.
"""


def get_privacy_policy() -> dict:
    from api.models import PengaturanInstitusi

    inst = PengaturanInstitusi.load()
    data = dict(PRIVACY_POLICY)
    data['konten'] = (inst.kebijakan or '').strip() or DEFAULT_KEBIJAKAN_MD
    return data
