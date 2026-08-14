PRIVACY_POLICY_VERSION = '1.1'
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
        'masa penyimpanan berakhir. NIK dan foto KTP tidak disimpan di profil.'
    ),
    'data_yang_disimpan': [
        {
            'kategori': 'Data identitas nasabah',
            'field': ['username', 'nama_lengkap', 'no_hp', 'alamat'],
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
    'data_yang_tidak_dikumpulkan': [
        'NIK',
        'Foto KTP pada profil / kartu digital',
        'Scan KTP otomatis / face recognition / data Dukcapil',
    ],
    'retensi': {
        'masa_tahun': RETENTION_YEARS,
        'keterangan': (
            'Data transaksi dan arsip digital disimpan minimal 5 tahun '
            'sesuai ketentuan tata kelola arsip OPD dan SOP bank sampah. '
            'Setelah masa retensi, data dapat dianonimkan atau dihapus '
            'sesuai keputusan pengelola. Lampiran foto KTP pada penarikan '
            'besar dihapus segera setelah pengajuan disetujui atau ditolak.'
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
            'status_saat_ini': 'tidak_disimpan',
            'opsional': True,
            'validasi_dukcapil': False,
            'implementasi': (
                'NIK tidak dikumpulkan dan tidak disimpan. Identitas operasional '
                'menggunakan nama, username/ID, nomor HP, dan alamat.'
            ),
        },
        'lampiran_ktp_penarikan_besar': {
            'tujuan': (
                'Verifikasi identitas saat pengajuan penarikan ≥ Rp1.000.000. '
                'Bukan arsip identitas permanen.'
            ),
            'akses': 'Hanya admin/koordinator, hanya saat status menunggu',
            'retensi': 'File dihapus setelah penarikan disetujui atau ditolak',
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
- Riwayat transaksi (setoran, penarikan, penukaran poin)
- Foto profil (jika diunggah)

NIK dan foto KTP **tidak** disimpan di akun. Foto KTP hanya dilampirkan sementara jika Anda mengajukan penarikan Rp1.000.000 atau lebih, lalu dihapus setelah petugas memproses pengajuan.

## 3. Tujuan Penggunaan

- Membuat dan mengelola akun
- Memproses setoran, penarikan, dan penukaran poin
- Menghubungi terkait jadwal penjemputan
- Pelaporan kepada pemerintah daerah

## 4. Penyimpanan dan Keamanan

Data disimpan di server yang aman. Data tidak dijual kepada pihak ketiga. Lampiran verifikasi penarikan besar tidak dipublikasikan dan tidak dikirim lewat notifikasi.

## 5. Hak Anda

- Mengakses dan memperbaiki data melalui aplikasi
- Mengajukan pengaduan terkait data atau layanan
- Meminta penjelasan penggunaan data kepada admin program

## 6. Masa Retensi

Data transaksi disimpan minimal 5 tahun sesuai tata kelola arsip. Lampiran foto KTP dihapus setelah penarikan selesai diproses. Setelah masa retensi transaksi, data dapat dianonimkan atau dihapus.

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
