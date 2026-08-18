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


DEFAULT_KEBIJAKAN_MD = """# Kebijakan Privasi (Privacy Policy)

**MIRU-G — Mimika Baru Green Solution**
Bank Sampah Resmi Distrik Mimika Baru, Kabupaten Mimika, Papua Tengah

**Versi:** 1.1 · **Dasar hukum:** Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi (UU PDP)

Terakhir diperbarui: sesuai tanggal publikasi di aplikasi.

---

## 1. Pendahuluan

MIRU-G ("kami", "Bank Sampah MIRU") berkomitmen melindungi data pribadi pengguna aplikasi mobile dan layanan terkait. Kebijakan Privasi ini menjelaskan jenis data yang kami kumpulkan, alasan pengumpulan, cara penyimpanan, hak Anda sebagai subjek data, serta cara menghubungi pengelola program.

Dengan mendaftar atau menggunakan aplikasi MIRU-G, Anda menyetujui kebijakan ini.

## 2. Ruang Lingkup

Kebijakan ini berlaku untuk:

- Aplikasi mobile MIRU-G (Android) untuk nasabah bank sampah
- Panel web administrasi MIRU-G (admin, koordinator, petugas, pemerintah distrik)
- Situs web publik MIRU-G (informasi layanan, edukasi, dan dokumen legal)

## 3. Data yang Kami Kumpulkan

### 3.1 Data identitas dan profil

- Username / ID nasabah
- Nama lengkap
- Nomor telepon (HP)
- Alamat domisili
- Foto profil (opsional, jika Anda mengunggah)

**NIK dan foto KTP tidak disimpan permanen di profil akun.**

### 3.2 Data transaksi dan layanan

- Riwayat setoran sampah (jenis, berat, nilai)
- Riwayat penarikan saldo dan penukaran poin/reward
- Permintaan penjemputan sampah (termasuk alamat/lokasi jemput)
- Pengaduan layanan
- Saldo dan poin program

### 3.3 Data teknis

- Token perangkat (FCM) untuk notifikasi push — jika Anda mengizinkan
- Log audit aktivitas akun (untuk keamanan dan akuntabilitas)
- Waktu persetujuan kebijakan data saat registrasi

### 3.4 Lampiran sementara

Untuk penarikan saldo **Rp1.000.000 atau lebih**, Anda dapat diminta melampirkan foto KTP sebagai verifikasi identitas. File ini:

- Hanya diakses admin/koordinator saat pengajuan menunggu
- **Tidak** disimpan sebagai arsip identitas permanen
- **Dihapus** setelah penarikan disetujui atau ditolak

## 4. Izin Aplikasi Mobile

Aplikasi MIRU-G dapat meminta izin perangkat berikut:

- **Internet** — sinkronisasi data, login, dan transaksi
- **Kamera** — foto profil, lampiran KTP penarikan besar, dokumentasi setoran
- **Lokasi** — alamat penjemputan sampah (GPS/koordinat)
- **Penyimpanan / Galeri** — memilih foto dari perangkat

Anda dapat menolak izin; beberapa fitur (misalnya unggah foto atau penjemputan berbasis lokasi) mungkin tidak berfungsi penuh.

## 5. Tujuan Penggunaan Data

Data pribadi digunakan untuk:

1. Registrasi, autentikasi, dan pengelolaan akun nasabah
2. Pencatatan setoran, penarikan, penukaran poin, dan bukti digital
3. Penjadwalan dan pelaksanaan penjemputan sampah
4. Notifikasi layanan (setoran, penjemputan, penarikan, pengumuman)
5. Penanganan pengaduan
6. Pelaporan operasional kepada Pemerintah Distrik Mimika Baru
7. Audit, keamanan sistem, dan kepatuhan regulasi

Kami **tidak menjual** data pribadi Anda kepada pihak ketiga.

## 6. Berbagi Data dengan Pihak Ketiga

Data dapat diproses oleh penyedia layanan teknis yang membantu operasional aplikasi, antara lain:

- **Firebase Cloud Messaging (Google)** — pengiriman notifikasi push
- **Penyedia hosting/server** — penyimpanan data aplikasi

Pihak ketiga hanya memproses data sesuai instruksi kami dan standar keamanan yang wajar. Data pemerintah daerah (laporan distrik) hanya dibagikan sesuai kewenangan resmi program bank sampah.

## 7. Penyimpanan dan Keamanan

- Data disimpan di server dengan kontrol akses berbasis peran (nasabah, petugas, admin)
- Koneksi aplikasi menggunakan enkripsi HTTPS
- Lampiran sensitif (foto KTP penarikan) tidak dipublikasikan dan tidak dikirim lewat notifikasi
- Audit log mencatat perubahan penting untuk transparansi

## 8. Masa Retensi Data

- **Data transaksi dan arsip digital:** minimal **5 (lima) tahun** sesuai tata kelola arsip OPD dan SOP bank sampah
- **Lampiran foto KTP penarikan besar:** dihapus segera setelah pengajuan selesai diproses
- **Token notifikasi:** dihapus saat logout/uninstall atau saat token tidak valid
- Setelah masa retensi, data dapat **dianonimkan atau dihapus** sesuai keputusan pengelola

## 9. Hak Subjek Data (UU PDP)

Anda berhak untuk:

- Mengakses dan memperbarui data profil melalui aplikasi
- Mengajukan pengaduan terkait data atau layanan
- Meminta penjelasan penggunaan data kepada admin program
- Menarik persetujuan (dengan konsekuensi tidak dapat melanjutkan layanan yang memerlukan data tersebut)

Permintaan dapat diajukan melalui fitur pengaduan di aplikasi atau kontak resmi di bawah.

## 10. Data Anak

Layanan MIRU-G ditujukan untuk warga/nasabah bank sampah. Jika pengguna berusia di bawah 18 tahun, pendaftaran sebaiknya didampingi orang tua/wali. Kami tidak dengan sengaja mengumpulkan data anak tanpa persetujuan wali yang sah.

## 11. Perubahan Kebijakan

Kami dapat memperbarui Kebijakan Privasi ini. Versi terbaru akan dipublikasikan di aplikasi dan situs web. Perubahan material dapat memerlukan persetujuan ulang saat login/registrasi.

## 12. Kontak Pengelola Data

**Bank Sampah MIRU — Distrik Mimika Baru**
Pemerintah Kabupaten Mimika

- Alamat: Jl. Cenderawasih Poros SP.II, Timika, Mimika Baru, Kabupaten Mimika, Papua Tengah 99910
- Telepon: 0821 977 3693
- Email: distrikmiru@mimikakab.go.id
- Jam layanan: Senin–Sabtu, 08.00–17.00 WIT

Untuk pertanyaan privasi, hubungi admin program melalui aplikasi (Pengaduan) atau kontak di atas.
"""

DEFAULT_SYARAT_MD = """# Syarat dan Ketentuan (Terms & Conditions)

**MIRU-G — Mimika Baru Green Solution**
Bank Sampah Resmi Distrik Mimika Baru, Kabupaten Mimika, Papua Tengah

**Versi:** 1.0

Terakhir diperbarui: sesuai tanggal publikasi di aplikasi.

---

## 1. Penerimaan Syarat

Dengan mengunduh, mendaftar, atau menggunakan aplikasi MIRU-G ("Aplikasi"), Anda ("Pengguna", "Nasabah") setuju terikat oleh Syarat dan Ketentuan ini beserta [Kebijakan Privasi](/privacy-policy) kami.

Jika Anda tidak setuju, mohon tidak menggunakan Aplikasi.

## 2. Definisi

- **MIRU-G / Bank Sampah MIRU:** program bank sampah resmi Distrik Mimika Baru yang dikelola Pemerintah Kabupaten Mimika.
- **Nasabah:** warga terdaftar yang menyetor sampah terpilah dan memiliki saldo/poin program.
- **Petugas / Koordinator / Admin:** pengguna panel web yang mengelola operasional bank sampah.
- **Setoran:** penyerahan sampah terpilah yang dicatat dalam sistem.
- **Saldo:** nilai rupiah hasil setoran yang dapat ditarik sesuai ketentuan.
- **Poin:** poin reward program yang dapat ditukar dengan hadiah/reward.

## 3. Layanan

MIRU-G menyediakan layanan digital antara lain:

1. Registrasi dan profil nasabah
2. Pencatatan setoran sampah terpilah
3. Permintaan penjemputan sampah
4. Informasi saldo, poin, dan riwayat transaksi
5. Pengajuan penarikan saldo
6. Penukaran poin/reward
7. Pengaduan layanan
8. Notifikasi dan edukasi sampah

Layanan dapat diubah, ditambah, atau dihentikan sebagian oleh pengelola demi kepentingan operasional, dengan pemberitahuan wajar jika memungkinkan.

## 4. Pendaftaran Akun

1. Nasabah wajib memberikan data yang **benar dan dapat dipertanggungjawabkan** (nama, nomor HP, alamat).
2. Nasabah wajib **menyetujui Kebijakan Privasi** saat registrasi.
3. Satu nasabah menggunakan satu akun; dilarang membuat akun palsu atau ganda untuk manipulasi saldo/poin.
4. Anda bertanggung jawab menjaga kerahasiaan kata sandi dan aktivitas pada akun Anda.
5. Segera laporkan jika akun dicurigai disalahgunakan.

## 5. Ketentuan Setoran Sampah

1. Sampah harus **terpilah** sesuai kategori yang ditetapkan bank sampah.
2. Berat dan jenis sampah dicatat petugas/koordinator; keputusan pencatatan mengacu pada prosedur operasional distrik.
3. Harga sampah mengikuti **tarif resmi** yang berlaku; perubahan harga akan diinformasikan melalui pengumuman.
4. Setoran fiktif, manipulasi berat, atau penyerahan sampah terlarang dapat mengakibatkan penolakan transaksi atau sanksi akun.

## 6. Saldo, Poin, dan Penarikan

1. Saldo dan poin dihitung berdasarkan setoran yang **disetujui/dicatat** dalam sistem.
2. Penarikan saldo mengikuti prosedur dan batas minimum/maksimum yang ditetapkan pengelola.
3. Penarikan **Rp1.000.000 atau lebih** dapat memerlukan verifikasi identitas (termasuk lampiran foto KTP sementara).
4. Pengelola berhak menunda atau menolak penarikan jika ditemukan indikasi pelanggaran, data tidak valid, atau kewajiban administrasi belum terpenuhi.
5. Poin reward memiliki masa berlaku sesuai ketentuan program; poin kadaluarsa tidak dapat ditukar kembali.

## 7. Penjemputan Sampah

1. Nasabah dapat mengajukan penjemputan melalui Aplikasi dengan alamat/lokasi yang akurat.
2. Jadwal penjemputan bergantung ketersediaan petugas dan wilayah layanan.
3. Nasabah wajib menyiapkan sampah terpilah saat petugas tiba.
4. Pembatalan atau perubahan jadwal sebaiknya dilakukan secepatnya melalui Aplikasi atau kontak petugas.

## 8. Pengaduan

Nasabah dapat mengajukan pengaduan terkait layanan atau data pribadi melalui fitur Pengaduan. Pengelola akan menindaklanjuti sesuai prosedur operasional dan ketentuan peraturan yang berlaku.

## 9. Penggunaan yang Dilarang

Pengguna dilarang:

- Mengakses sistem tanpa otorisasi atau mencoba mengganggu keamanan server
- Menyalahgunakan fitur untuk penipuan, pencucian data, atau manipulasi saldo/poin
- Mengunggah konten ilegal, menyesatkan, atau melanggar hak pihak ketiga
- Menyebarkan malware atau melakukan scraping otomatis terhadap layanan

Pelanggaran dapat mengakibatkan **penangguhan atau penghapusan akun** serta tindakan sesuai hukum.

## 10. Kekayaan Intelektual

Nama MIRU-G, logo, desain antarmuka, dan materi edukasi adalah milik pengelola/pemerintah distrik. Dilarang menyalin, memodifikasi, atau mendistribusikan tanpa izin tertulis, kecuali untuk penggunaan pribadi non-komersial yang diizinkan.

## 11. Batasan Tanggung Jawab

1. Aplikasi disediakan **"sebagaimana adanya"** untuk mendukung operasional bank sampah.
2. Pengelola berupaya menjaga ketersediaan sistem, namun tidak menjamin layanan bebas gangguan (misalnya pemadaman jaringan, pemeliharaan server).
3. Pengelola tidak bertanggung jawab atas kerugian tidak langsung akibat force majeure, kesalahan jaringan pihak ketiga, atau kelalaian pengguna menjaga keamanan akun.
4. Keputusan operasional di lapangan (penerimaan jenis sampah, verifikasi setoran) mengacu pada SOP resmi distrik.

## 12. Penangguhan dan Penghapusan Akun

Pengelola dapat menangguhkan atau menghapus akun jika:

- Terbukti melanggar Syarat dan Ketentuan
- Data registrasi palsu atau menyesatkan
- Tidak ada aktivitas dalam jangka waktu lama (sesuai kebijakan internal)
- Atas permintaan resmi aparat sesuai hukum

Nasabah dapat meminta penghapusan akun melalui pengaduan; data tertentu dapat tetap disimpan sesuai kewajiban retensi arsip (lihat Kebijakan Privasi).

## 13. Perubahan Syarat

Syarat dan Ketentuan dapat diperbarui. Versi terbaru dipublikasikan di situs web dan/atau Aplikasi. Penggunaan berkelanjutan setelah perubahan dianggap sebagai penerimaan syarat yang diperbarui.

## 14. Hukum yang Berlaku

Syarat ini tunduk pada hukum Republik Indonesia, termasuk UU Perlindungan Data Pribadi. Sengketa diselesaikan secara musyawarah; jika tidak tercapai, melalui mekanisme hukum yang berlaku di Kabupaten Mimika.

## 15. Kontak

**Bank Sampah MIRU — Distrik Mimika Baru**

- Alamat: Jl. Cenderawasih Poros SP.II, Timika, Mimika Baru, Kabupaten Mimika, Papua Tengah 99910
- Telepon: 0821 977 3693
- Email: distrikmiru@mimikakab.go.id
- Jam layanan: Senin–Sabtu, 08.00–17.00 WIT
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


TERMS_OF_SERVICE_VERSION = '1.0'

TERMS_OF_SERVICE = {
    'versi': TERMS_OF_SERVICE_VERSION,
    'judul': 'Syarat dan Ketentuan MIRU-G',
    'institusi': 'Bank Sampah MIRU — Distrik Mimika Baru',
    'ringkasan': (
        'Syarat penggunaan aplikasi MIRU-G untuk nasabah bank sampah: '
        'pendaftaran akun, setoran sampah, saldo/poin, penarikan, '
        'penjemputan, dan tata cara pengaduan layanan.'
    ),
}


def get_terms_of_service() -> dict:
    from api.models import PengaturanInstitusi

    inst = PengaturanInstitusi.load()
    data = dict(TERMS_OF_SERVICE)
    data['konten'] = (inst.syarat_ketentuan or '').strip() or DEFAULT_SYARAT_MD
    return data
