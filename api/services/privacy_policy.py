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


def get_privacy_policy() -> dict:
    return PRIVACY_POLICY
