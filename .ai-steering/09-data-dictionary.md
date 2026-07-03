# 09 — Data Dictionary & Reference Values (Backend)

> **Sumber:** Dokumen jawaban klien (2 Juli 2026), SOP Aplikasi MIRU Bank Sampah, dan Proposal

---

## A. KATEGORI & HARGA SAMPAH (Seed Data)

### A.1 Daftar Jenis Sampah yang Diterima

| No | Kategori | Contoh Sampah | Harga Acuan (Rp/kg) | Keterangan |
|----|----------|---------------|--------------------|------------|
| 1 | **Plastik PET** | Botol air mineral | **Rp3.000** | Harga wajib disesuaikan pengepul lokal Timika |
| 2 | **Gelas Plastik** | Gelas minuman | **Rp4.000** | Harga wajib disesuaikan pengepul lokal Timika |
| 3 | **Kardus** | Kardus kemasan | **Rp1.500** | Harga wajib disesuaikan pengepul lokal Timika |
| 4 | **Kertas Putih** | Kertas HVS, buku bekas | **Rp2.000** | Harga wajib disesuaikan pengepul lokal Timika |
| 5 | **Aluminium** | Kaleng aluminium | **Rp10.000** | Harga wajib disesuaikan pengepul lokal Timika |
| 6 | **Besi/Logam** | Besi tua, kaleng | **Rp3.000** | Harga wajib disesuaikan pengepul lokal Timika |
| 7 | **Kaca** | Botol sirup/kecap | **Rp500** | Harga wajib disesuaikan pengepul lokal Timika |
| 8 | **Minyak Jelantah** | Minyak goreng bekas | **Rp5.000/liter** | Satuan liter, bukan kg |
| 9 | **Organik** | Sisa makanan, daun | (menyusul) | Belum ada harga pasti tahap awal |
| 10 | **Elektronik** | Barang elektronik rusak | (menyusul) | Belum ada harga pasti tahap awal |

> **⚠️ Catatan Penting:** Harga di atas adalah **contoh acuan awal**. Harga **WAJIB disesuaikan dengan harga pengepul lokal Timika** sebelum peluncuran. Harga dievaluasi bulanan dan perubahan diumumkan minimal 3 hari sebelum berlaku.

### A.2 Ketentuan Kategori
- Minimal setoran per jenis: **1 kg**
- Sampah sebaiknya dalam kondisi **kering dan bersih**
- Sampah dipisahkan sesuai jenis
- Sampah berbahaya harus dilaporkan kepada petugas
- Sampah yang tidak layak dapat **ditolak** oleh petugas

---

## B. KATALOG REWARD (Seed Data)

| No | Reward | Poin Dibutuhkan | Setara Nilai |
|----|--------|-----------------|--------------|
| 1 | Pulsa Rp10.000 | **100 poin** | ± Rp10.000 |
| 2 | Bibit Tanaman | **50 poin** | ± Rp5.000 |
| 3 | Sembako (beras, gula, minyak) | **250 poin** | ± Rp25.000 |
| 4 | Alat Kebersihan | **300 poin** | ± Rp30.000 |

> Daftar reward **final sesuai anggaran** yang tersedia dan dapat diubah oleh admin. Penukaran di kantor bank sampah pada jam layanan. Poin **tidak dapat diuangkan**. Masa berlaku poin: **1 tahun**.

---

## C. KONVERSI & ATURAN KEUANGAN

### C.1 Konversi Setoran
```
Saldo Bertambah = Σ (Berat_kg × Harga_per_kg)
Poin Bertambah = floor(Total_Nilai_Setoran / 1000)
```

### C.2 Contoh Perhitungan (dari SOP)

| Jenis Sampah | Berat | Harga/Kg | Total |
|--------------|-------|----------|-------|
| Plastik Botol | 5 kg | Rp2.000 | Rp10.000 |
| Kardus | 3 kg | Rp1.500 | Rp4.500 |
| Kaleng | 2 kg | Rp3.000 | Rp6.000 |
| **Total Saldo Masuk** | | | **Rp20.500** |
| **Poin Didapat** | | | **20 poin** |

### C.3 Aturan Keuangan Ringkas

| Aturan | Nilai |
|--------|-------|
| Minimal setoran per jenis | **1 kg** |
| Minimal estimasi penjemputan | **5 kg** |
| Minimal penarikan saldo | **Rp50.000** |
| Konversi saldo → poin | **1 poin per Rp1.000** |
| 100 poin ≈ | **Rp10.000 nilai reward** |
| Masa berlaku poin | **1 tahun (12 bulan)** |
| Akumulasi saldo | **Tanpa batas waktu** |
| Metode pencairan tahap awal | **Tunai di kantor** |
| Metode pencairan tahap lanjut | **Transfer bank / e-wallet** (future) |

---

## D. JAM LAYANAN & OPERASIONAL

| Hari | Jam | Keterangan |
|------|-----|------------|
| Senin – Sabtu | **08.00 – 17.00 WIT** | Jam layanan kantor & bank sampah |
| Minggu | **Libur** | - |
| Penjemputan | **Max 2x/minggu/wilayah** | Pesan minimal H-1 via aplikasi |
| Penjemputan tahap awal | **Terbatas kelurahan sekitar kantor** | Diperluas bertahap |

> WIT = Waktu Indonesia Timur (UTC+9)

---

## E. STANDAR WAKTU PELAYANAN (dari SOP)

| Layanan | Standar Waktu |
|---------|---------------|
| Verifikasi pendaftaran nasabah | **Maksimal 1 hari kerja** |
| Input transaksi setoran langsung | **Pada hari yang sama** |
| Konfirmasi penjemputan | **Maksimal 1 hari kerja** |
| Penyelesaian penjemputan | **Sesuai jadwal yang disetujui** |
| Penarikan saldo | **Maksimal 1–2 hari kerja** |
| Penanganan pengaduan ringan | **Maksimal 2 hari kerja** |
| Laporan bulanan | **Akhir bulan berjalan** |
| Target penyelesaian pengaduan | **100% ditindaklanjuti** |

---

## F. INDIKATOR KEBERHASILAN PROGRAM (dari SOP)

| Indikator | Target |
|-----------|--------|
| Jumlah nasabah aktif | **Meningkat setiap bulan** |
| Total sampah terkumpul | **Meningkat setiap bulan** |
| Jumlah penjemputan selesai | **Meningkat sesuai permintaan** |
| Jumlah RT/RW aktif | **Bertambah secara bertahap** |
| Nilai ekonomi sampah | **Meningkat setiap bulan** |
| Pengaduan terselesaikan | **Minimal 90% selesai** |
| Laporan bulanan | **Tersedia tepat waktu** |

---

## G. STANDAR ETIKA PETUGAS (dari SOP)

1. Melayani masyarakat dengan **sopan, ramah, dan profesional**
2. Menimbang sampah secara **jujur dan transparan**
3. **Tidak melakukan pungutan** di luar ketentuan
4. **Menjaga kerahasiaan** data nasabah
5. Menggunakan akun aplikasi **sesuai kewenangan**
6. **Menjaga kebersihan** lokasi bank sampah
7. **Melaporkan kendala** kepada admin atau koordinator

---

## H. FORMAT & JADWAL LAPORAN

### H.1 Isi Laporan
| Komponen | Keterangan |
|----------|------------|
| Jumlah nasabah terdaftar | Total akun aktif |
| Jumlah nasabah aktif | Bertransaksi dalam periode tersebut |
| Total sampah terkumpul | Tonase per jenis sampah |
| Total nilai ekonomi sampah | Rupiah dari setoran |
| Jumlah penjemputan | Total pickup selesai |
| Jumlah saldo nasabah | Total saldo beredar |
| Jumlah reward diberikan | Poin & reward yang sudah ditukar |
| Wilayah RT/RW paling aktif | Kelurahan dengan partisipasi tertinggi |
| Kendala lapangan | Masalah operasional yang ditemui |
| Rekomendasi tindak lanjut | Saran perbaikan program |

### H.2 Jadwal Laporan
| Jenis Laporan | Waktu |
|--------------|-------|
| Laporan Harian | Setiap akhir hari kerja |
| Laporan Mingguan | Setiap akhir minggu |
| Laporan Bulanan | Setiap akhir bulan (12x/tahun) |
| Laporan Tahunan | Akhir tahun anggaran |
| Laporan Evaluasi | Sesuai kebutuhan pimpinan |

---

## I. DATA ORGANISASI & APLIKASI

### I.1 Identitas Aplikasi
| Item | Nilai |
|------|-------|
| Nama Aplikasi | **MIRU Bank Sampah (Miru-G)** |
| Nama Lengkap | Aplikasi Inovasi Bank Sampah Distrik Mimika Baru "MIRU BANK SAMPAH" |
| Slogan | "Sampah Bernilai, Lingkungan Bersih, Warga Sejahtera" |
| Motto Distrik | "Melayani Dengan Hati — Cepat, Tepat, Transparan & Akuntabel" |
| Deskripsi | Aplikasi bank sampah Distrik Mimika Baru — setor sampah, dapat saldo & poin |
| Platform | Web Admin + Android (prioritas), iOS (menyusul) |

### I.2 Pengelola
| Jabatan | Nama |
|---------|------|
| Penanggung Jawab | **Merlyn Temorubun, S,STP** (Kepala Distrik) |
| Koordinator Program | **Arfan** |
| Admin Sistem | **Harorld Sopacua** |
| Developer | **PT Webekspres Teknologi Indonesia** |

### I.3 Kontak
| Jenis | Detail |
|-------|--------|
| Telepon/WA | **0821 977 3693** |
| Email Instansi | **distrikmiru@mimikakab.go.id** |
| Email Layanan | **distrikmiru72@gmail.com** |
| Alamat | Jl. Cendrawasih Poros SP.II, Timika, Papua Tengah 99910 |
| Website Developer | webekspres.id |

### I.4 Domain & Server
| Item | Status |
|------|--------|
| Domain usulan | mirubanksampah.id / miru-g.id / subdomain pemda |
| Server | Layanan Webekspres |
| SSL/HTTPS | Wajib, disediakan bersama hosting |
| Backup | Harian (database) + Mingguan (full), retensi 30 hari |

---

## J. JENIS PENGADUAN (dari SOP)

| No | Jenis Pengaduan |
|----|----------------|
| 1 | Saldo belum masuk |
| 2 | Jadwal penjemputan terlambat |
| 3 | Berat sampah tidak sesuai |
| 4 | Harga sampah tidak sesuai |
| 5 | Petugas tidak datang |
| 6 | Kesalahan data nasabah |
| 7 | Bukti transaksi tidak muncul |

---

## K. WILAYAH LAYANAN

| Item | Detail |
|------|--------|
| Wilayah penuh | Seluruh kelurahan/kampung di **Distrik Mimika Baru** |
| Target layanan | RT/RW, sekolah, kantor pemerintah, pelaku usaha (ruko/warung) |
| Penjemputan tahap awal | **Terbatas** pada kelurahan sekitar kantor distrik |
| Perluasan | Dilakukan **bertahap** sesuai kemampuan operasional |
| Rincian RT/RW prioritas | Akan dilampirkan oleh pengelola |
