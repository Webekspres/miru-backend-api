PRIVACY_POLICY_VERSION = '2.0'
TERMS_OF_SERVICE_VERSION = '1.0'
RETENTION_YEARS = 5

PRIVACY_POLICY = {
    'versi': PRIVACY_POLICY_VERSION,
    'judul': 'Kebijakan Data Pribadi MIRU Bank Sampah',
    'institusi': 'Bank Sampah MIRU — Distrik Mimika Baru',
    'dasar_hukum': 'Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi (UU PDP)',
    'ringkasan': (
        'MIRU Bank Sampah mengumpulkan data pribadi nasabah dan petugas '
        'secara terbatas untuk operasional program bank sampah, disimpan '
        'dengan aman, dan tidak pernah dijual kepada pihak ketiga. Nasabah '
        'berhak mengakses, memperbaiki, hingga menghapus akun beserta data '
        'pribadinya melalui aplikasi atau website. NIK dan foto KTP tidak '
        'disimpan di profil. Catatan transaksi dipertahankan maksimal 5 tahun '
        'sebagai arsip keuangan bank sampah sesuai ketentuan perundangan.'
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
            'kategori': 'Data audit & keamanan',
            'field': ['audit log', 'riwayat harga', 'persetujuan kebijakan'],
            'tujuan': 'Transparansi, akuntabilitas, dan kepatuhan regulasi',
        },
        {
            'kategori': 'Data teknis & perangkat',
            'field': ['device token FCM', 'stempel waktu akses'],
            'tujuan': 'Pengiriman notifikasi dan pengamanan sesi akun',
        },
    ],
    'data_yang_tidak_dikumpulkan': [
        'NIK',
        'Foto KTP pada profil / kartu digital',
        'Scan KTP otomatis / face recognition / data Dukcapil',
        'Riwayat lokasi GPS secara berkala',
        'Kontak ponsel / galeri / mikrofon',
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
        'Memperbaiki atau melengkapi data yang tidak akurat',
        'Meminta penjelasan penggunaan data kepada admin program',
        'Mengajukan pengaduan terkait data atau layanan',
        'Menarik persetujuan pemrosesan data kapan saja',
        'Menghapus akun beserta data pribadi melalui aplikasi atau website',
    ],
    'penghapusan_akun': {
        'cara': [
            'Melalui aplikasi mobile (menu Profil) atau halaman website /hapus-akun',
            'Verifikasi kepemilikan dengan OTP WhatsApp (seperti saat login)',
            'Konfirmasi tertulis (ketik frasa konfirmasi) sebelum akun dihapus',
        ],
        'akibat': (
            'Akun dinonaktifkan, data pribadi dianonimkan/dihapus, saldo dan '
            'poin dinolkan, dan pengguna tidak dapat login kembali.'
        ),
        'dipertahankan': (
            'Catatan transaksi (setoran, penjemputan, penarikan, penukaran '
            'poin, pengaduan) dipertahankan sebagai arsip keuangan bank '
            'sampah sesuai Pasal 26 UU PDP (kepentingan hukum/operasional), '
            'tanpa menautkan kembali ke identitas pribadi setelah dianonimkan.'
        ),
    },
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


TERMS = {
    'versi': TERMS_OF_SERVICE_VERSION,
    'judul': 'Syarat & Ketentuan MIRU Bank Sampah',
    'institusi': 'Bank Sampah MIRU — Distrik Mimika Baru',
    'dasar_hukum': 'Hukum Republik Indonesia, termasuk UU Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi',
    'ringkasan': (
        'Syarat & Ketentuan ini mengatur penggunaan aplikasi dan layanan '
        'MIRU Bank Sampah oleh nasabah, termasuk pendaftaran akun, setoran, '
        'penjemputan, saldo & poin, penarikan, penukaran reward, pengaduan, '
        'serta hak dan kewajiban pengguna. Dengan mendaftar atau menggunakan '
        'layanan, Anda dianggap telah membaca dan menyetujui seluruh ketentuan '
        'di bawah ini.'
    ),
}


DEFAULT_KEBIJAKAN_MD = """# Kebijakan Perlindungan Data Pribadi

**MIRU Bank Sampah** — Distrik Mimika Baru

Berlaku sesuai **Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi (UU PDP)**.

---

## 1. Pendahuluan

MIRU Bank Sampah (selanjutnya disebut "kami") berkomitmen melindungi data pribadi setiap nasabah, petugas, dan pengguna layanan. Kebijakan ini menjelaskan secara terbuka:

- data pribadi apa saja yang kami kumpulkan;
- untuk apa data tersebut digunakan;
- bagaimana data disimpan, dilindungi, dan berapa lama disimpan;
- hak-hak Anda sebagai pemilik data pribadi, termasuk cara menghapus akun.

Dengan mendaftar akun atau menggunakan layanan MIRU Bank Sampah, Anda menyatakan setuju terhadap pemrosesan data pribadi sesuai kebijakan ini.

## 2. Dasar Hukum

Pemrosesan data pribadi dalam sistem ini dilakukan berdasarkan:

1. **Undang-Undang Nomor 27 Tahun 2022** tentang Pelindungan Data Pribadi (UU PDP);
2. Peraturan perundang-undangan terkait arsip dan tata kelola keuangan daerah;
3. SOP pengelolaan bank sampah Distrik Mimika Baru;
4. Persetujuan (consent) yang Anda berikan saat registrasi, yang waktu persetujuannya kami catat di sistem.

## 3. Data Pribadi yang Dikumpulkan

Kami hanya mengumpulkan data yang benar-benar diperlukan untuk menyelenggarakan layanan bank sampah:

| Kategori | Data | Tujuan |
|---|---|---|
| Identitas akun | Username, nama lengkap, nomor HP, alamat, RT/RW/kelurahan | Registrasi, identifikasi saat setoran, komunikasi layanan |
| Keuangan program | Saldo, poin | Perhitungan hak Anda atas hasil setoran dan reward |
| Transaksi | Setoran, penjemputan, penarikan, penukaran poin, pengaduan | Pencatatan operasional dan bukti digital |
| Audit | Audit log, riwayat harga, waktu persetujuan kebijakan | Transparansi, akuntabilitas, kepatuhan regulasi |
| Teknis | Token perangkat (FCM), stempel waktu akses | Pengiriman notifikasi dan pengamanan sesi |

**Data yang TIDAK kami kumpulkan:** NIK, foto KTP pada profil/kartu digital, scan KTP otomatis, face recognition, data Dukcapil, riwayat lokasi GPS berkala, kontak ponsel, galeri, maupun mikrofon.

> Foto KTP hanya dilampirkan **sementara** saat Anda mengajukan penarikan Rp1.000.000 atau lebih, dan **dihapus segera** setelah pengajuan disetujui atau ditolak oleh petugas.

## 4. Tujuan dan Dasar Pemrosesan

Data pribadi diproses semata-mata untuk:

- membuat dan mengelola akun Anda;
- memproses setoran, penjemputan, penarikan saldo, dan penukaran poin;
- menghubungi Anda terkait jadwal penjemputan atau status layanan;
- menyusun laporan agregat untuk Pemerintah Distrik dan OPD terkait;
- menjaga keamanan sistem dan mencegah penyalahgunaan akun.

Kami **tidak pernah menjual** data pribadi kepada pihak ketiga, dan tidak menggunakannya untuk iklan lintas platform.

## 5. Penyimpanan dan Keamanan

- Data disimpan pada server yang dikelola dengan kontrol akses berlapis;
- Kata sandi disimpan dalam bentuk ter-hash, tidak pernah dalam teks terbuka;
- Kode OTP disimpan sebagai hash dan hanya berlaku 5 menit;
- Setiap perubahan data penting tercatat dalam audit log;
- Akses data nasabah oleh petugas dibatasi sesuai peran dan kebutuhan kerja.

## 6. Masa Retensi Data

- **Catatan transaksi** dan arsip digital disimpan **minimal 5 tahun** sesuai tata kelola arsip OPD dan SOP bank sampah;
- **Lampiran foto KTP** penarikan besar dihapus segera setelah diproses;
- **Data profil** yang sudah tidak aktif dapat dianonimkan atau dihapus sesuai keputusan pengelola;
- Setelah masa retensi berakhir, data dianonimkan atau dihapus permanen.

## 7. Hak Anda sebagai Pemilik Data

Berdasarkan UU PDP, Anda berhak untuk:

1. **Mengakses** data pribadi Anda;
2. **Memperbaiki / melengkapi** data yang tidak akurat;
3. **Menghapus** data pribadi Anda (termasuk melalui fitur hapus akun);
4. **Menarik persetujuan** pemrosesan data kapan saja;
5. **Mengajukan keberatan / pembatasan** pemrosesan;
6. **Mengajukan pengaduan** terkait pemrosesan data;
7. Menuntut **ganti rugi** apabila terjadi pelanggaran sesuai ketentuan perundang-undangan.

## 8. Penghapusan Akun

Anda dapat menghapus akun beserta data pribadi Anda kapan saja melalui:

1. **Aplikasi mobile** — menu Profil, lalu pilih Hapus Akun; atau
2. **Website** — halaman `https://(domain)/hapus-akun`.

Demi keamanan, proses penghapusan mewajibkan:

- verifikasi kepemilikan melalui **OTP WhatsApp** (sama seperti saat login);
- konfirmasi nomor HP terdaftar; dan
- konfirmasi tertulis bahwa Anda memahami tindakan ini **permanen**.

Setelah penghapusan: akun dinonaktifkan, data pribadi dianonimkan/dihapus, saldo dan poin dinolkan, dan Anda tidak dapat login kembali.

**Catatan penting:** berdasarkan **Pasal 26 UU PDP**, kami dapat mempertahankan catatan transaksi (setoran, penjemputan, penarikan, penukaran poin, pengaduan) sebagai arsip keuangan bank sampah yang sah, **tanpa menautkan kembali ke identitas pribadi** Anda setelah dianonimkan. Data yang dipertahankan tidak digunakan untuk keperluan lain.

## 9. Berbagi Data

Data hanya dibagikan dalam lingkup:

- **Petugas/Admin/Koordinator** bank sampah — sebatas yang diperlukan untuk melayani Anda;
- **Pemerintah Distrik Mimika Baru** — dalam bentuk laporan agregat untuk evaluasi program;
- **Penyedia layanan teknis** (misal penyimpanan cloud, gateway WhatsApp) — sebatas kontrak kerja, tanpa hak menggunakan data di luar kepentingan layanan.

## 10. Perubahan Kebijakan

Kebijakan ini dapat diperbarui sewaktu-waktu. Perubahan substansial akan diumumkan melalui aplikasi dan/atau website. Versi terbaru selalu tersedia di halaman Kebijakan Privasi. Dengan tetap menggunakan layanan setelah perubahan, Anda dianggap menyetujui kebijakan terbaru.

## 11. Kontak dan Pengaduan

Untuk pertanyaan, koreksi data, atau pengaduan terkait perlindungan data pribadi, hubungi:

- **Kantor:** Distrik Mimika Baru, Kabupaten Mimika, Papua Tengah
- **Kontak:** 0821 977 3693
- **Email:** distrikmiru@mimikakab.go.id

Kami akan menindaklanjuti setiap permintaan sesuai ketentuan UU PDP.
"""


DEFAULT_SYARAT_MD = """# Syarat & Ketentuan

**MIRU Bank Sampah** — Distrik Mimika Baru

Berlaku sejak tanggal diumumkan dan mengikat setiap pengguna layanan.

---

## 1. Penerimaan Syarat

Dengan mendaftar akun, mengunduh, atau menggunakan aplikasi/website MIRU Bank Sampah, Anda dianggap telah membaca, memahami, dan menyetujui seluruh Syarat & Ketentuan ini beserta Kebijakan Perlindungan Data Pribadi. Jika tidak setuju, mohon tidak menggunakan layanan ini.

## 2. Definisi

- **Nasabah** — pengguna aplikasi mobile (masyarakat) yang memiliki akun MIRU.
- **Petugas / Admin / Koordinator** — pengelola bank sampah yang bertugas melayani operasional.
- **Saldo** — nilai rupiah hasil setoran sampah yang menjadi hak nasabah.
- **Poin** — satuan reward yang diperoleh dari transaksi setoran dan dapat ditukar dengan hadiah.
- **Layanan** — seluruh fitur: setoran, penjemputan, saldo & poin, penarikan, penukaran reward, dan pengaduan.

## 3. Pendaftaran Akun

- Pendaftaran dilakukan dengan data yang **benar, lengkap, dan dapat dipertanggungjawabkan**.
- Nomor HP diverifikasi melalui **OTP WhatsApp**; satu nomor HP mewakili satu akun.
- Anda bertanggung jawab penuh atas kerahasiaan username dan kata sandi akun.
- Pengelola berhak menolak atau menonaktifkan akun yang terdaftar dengan identitas palsu atau untuk tujuan melanggar hukum.

## 4. Layanan Bank Sampah

1. **Setoran sampah terpilah** — sampah plastik, kertas, logam, dan jenis lain yang diterima sesuai ketentuan; hasil setoran masuk sebagai saldo dan poin.
2. **Penjemputan** — penjadwalan jemput sampah oleh petugas di alamat yang terdaftar; hanya untuk wilayah layanan yang aktif.
3. **Saldo & poin** — saldo dapat ditarik tunai/rekening; poin dapat ditukar dengan reward selama masa berlaku (1 tahun).
4. **Penarikan saldo** — penarikan Rp1.000.000 atau lebih wajib melampirkan foto KTP untuk verifikasi; foto dihapus setelah diproses.
5. **Pengaduan** — nasabah dapat melaporkan kendala layanan melalui aplikasi dan akan ditindaklanjuti petugas.

## 5. Hak dan Kewajiban Nasabah

**Kewajiban:**

- Menjaga keakuratan data profil dan segera memperbarui jika berubah;
- Tidak menggunakan akun untuk aktivitas ilegal, penipuan, atau penyalahgunaan layanan;
- Menjaga kerahasiaan kredensial akun;
- Mematuhi ketentuan jenis dan berat minimal sampah yang diterima.

**Hak:**

- Mengakses ringkasan saldo, poin, dan riwayat transaksi;
- Mengajukan penjemputan, penarikan, dan penukaran poin;
- Mengajukan pengaduan dan memperoleh tanggapan;
- Memperbarui atau menghapus akun sesuai ketentuan yang berlaku.

## 6. Saldo, Poin, dan Reward

- Nilai setoran dihitung berdasarkan **harga resmi per kilogram** yang diumumkan dan mulai berlaku sesuai ketentuan perubahan harga (H+3);
- Poin diberikan berdasarkan nilai setoran dan berlaku **1 tahun** sejak diperoleh; poin yang tidak digunakan akan hangus otomatis;
- Penukaran reward mengikuti stok yang tersedia dan keputusan pengelola;
- Kesalahan pencatatan dapat dikoreksi oleh pengelola melalui mekanisme yang sah dan tercatat di audit log.

## 7. Penghentian dan Penghapusan Akun

- **Anda** dapat menghapus akun kapan saja melalui aplikasi (menu Profil) atau halaman website `/hapus-akun` dengan verifikasi OTP WhatsApp dan konfirmasi tertulis.
- **Pengelola** berhak menonaktifkan akun apabila melanggar ketentuan ini, terlibat penipuan, atau berdasarkan ketentuan hukum.
- Penghapusan akun bersifat permanen; saldo dan poin yang tersisa tidak dapat dikembalikan setelah proses selesai.
- Catatan transaksi tetap dipertahankan sebagai arsip keuangan bank sampah sesuai peraturan perundang-undangan.

## 8. Pembatasan Tanggung Jawab

- Layanan disediakan sebagaimana adanya; pengelola berupaya menjaga ketersediaan dan keakuratan data;
- Pengelola tidak bertanggung jawab atas kerugian akibat kelalaian nasabah (misal membagikan kredensial akun) atau force majeure;
- Pengelola tidak bertanggung jawab atas keputusan pengguna yang bertentangan dengan ketentuan ini.

## 9. Perubahan Syarat

Syarat & Ketentuan dapat diperbarui sewaktu-waktu. Perubahan akan diumumkan melalui aplikasi dan/atau website, dan versi terbaru selalu tersedia di halaman ini. Penggunaan layanan setelah perubahan berarti menyetujui ketentuan terbaru.

## 10. Hukum yang Berlaku

Syarat & Ketentuan ini tunduk pada hukum Republik Indonesia, termasuk UU Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi. Sengketa diupayakan diselesaikan secara musyawarah terlebih dahulu, dan apabila tidak tercapai diselesaikan melalui mekanisme yang berlaku di wilayah hukum Kabupaten Mimika.

## 11. Kontak

- **Kantor:** Distrik Mimika Baru, Kabupaten Mimika, Papua Tengah
- **Kontak:** 0821 977 3693
- **Email:** distrikmiru@mimikakab.go.id
"""


DEFAULT_TENTANG_MD = """# Tentang MIRU

**MIRU (Mimika Recycle Unit)** adalah aplikasi bank sampah resmi **Distrik Mimika Baru**, Kabupaten Mimika, Papua Tengah — bagian dari program inovasi daerah dalam pengelolaan sampah.

> **"Sampah Bernilai, Lingkungan Bersih, Warga Sejahtera"**

## Apa itu MIRU Bank Sampah?

MIRU Bank Sampah adalah sistem digital yang menghubungkan masyarakat (nasabah), petugas bank sampah, dan Pemerintah Distrik dalam satu ekosistem pengelolaan sampah. Sampah yang tadinya dianggap tidak bernilai, melalui MIRU dikelola menjadi **nilai ekonomi** bagi warga sekaligus menjaga kebersihan lingkungan.

## Visi & Misi

- **Visi:** Mewujudkan Distrik Mimika Baru yang bersih, sehat, dan sejahtera melalui pengelolaan sampah berbasis masyarakat.
- **Misi:**
  1. Meningkatkan kesadaran masyarakat dalam memilah sampah;
  2. Memberikan nilai ekonomi langsung dari setoran sampah;
  3. Mewujudkan tata kelola bank sampah yang transparan dan akuntabel;
  4. Mendukung target pengurangan sampah daerah.

## Layanan Utama

- **Setoran sampah terpilah** — plastik, kertas, logam, dan minyak jelantah dengan penimbangan resmi;
- **Penjemputan** — jadwal jemput sampah oleh petugas bank sampah di rumah;
- **Saldo & poin** — hasil setoran tersimpan sebagai saldo yang dapat ditarik, serta poin yang dapat ditukar reward;
- **Kartu digital (QR)** — identitas nasabah untuk transaksi cepat dan akurat;
- **Pengaduan** — saluran laporan kendala layanan yang ditindaklanjuti petugas;
- **Edukasi sampah** — artikel dan panduan memilah sampah untuk warga.

## Cara Kerja

1. **Daftar** — buat akun melalui aplikasi mobile dan verifikasi nomor HP;
2. **Setor** — bawa sampah terpilah ke bank sampah atau ajukan penjemputan;
3. **Catat** — petugas menimbang, mencatat nilai, dan saldo/poin bertambah otomatis;
4. **Tarik/Tukar** — saldo dapat ditarik atau poin ditukar reward;
5. **Pantau** — seluruh riwayat transaksi dapat dilihat kapan saja di aplikasi.

## Teknologi

Dikembangkan oleh **PT Webekspres Teknologi Indonesia** untuk Pemerintah Distrik Mimika Baru. Sistem terdiri dari aplikasi mobile untuk nasabah, panel web untuk petugas/admin, dan API terpusat yang aman (JWT + enkripsi data pribadi).

## Wilayah Layanan

Layanan MIRU Bank Sampah beroperasi di wilayah kerja **Distrik Mimika Baru, Kabupaten Mimika, Papua Tengah** sesuai daftar kelurahan/kampung yang aktif di sistem.

## Kontak

- **Kantor:** Distrik Mimika Baru, Kabupaten Mimika, Papua Tengah
- **Kontak:** 0821 977 3693
- **Email:** distrikmiru@mimikakab.go.id
- **Jam Operasional:** Senin–Sabtu, 08.00–17.00 WIT
"""


def get_privacy_policy() -> dict:
    from api.models import PengaturanInstitusi

    inst = PengaturanInstitusi.load()
    data = dict(PRIVACY_POLICY)
    data['konten'] = (inst.kebijakan or '').strip() or DEFAULT_KEBIJAKAN_MD
    return data


def get_terms_of_service() -> dict:
    from api.models import PengaturanInstitusi

    inst = PengaturanInstitusi.load()
    data = dict(TERMS)
    data['konten'] = (
        (inst.syarat_ketentuan or '').strip() or DEFAULT_SYARAT_MD
    )
    return data
