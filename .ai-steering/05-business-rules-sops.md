# 05 — Business Rules & SOPs

## A. Aturan Keuangan

### A.1 Konversi Setoran ke Saldo
```
Total Saldo = Σ (berat_kg × harga_saat_itu) untuk setiap kategori
```
- Harga per kg diambil dari `KategoriSampah.harga_beli_per_kg` saat transaksi.
- Harga disimpan di `DetailSetoran.harga_saat_itu` untuk menjaga riwayat harga.
- Minimal setoran per jenis sampah: **1 kg**.

### A.2 Konversi Saldo ke Poin Reward
```
Poin = floor(Total Nilai Setoran / 1000)
```
- Setiap Rp1.000 nilai setoran = **1 poin reward**.
- Poin hanya dari setoran, bukan dari top-up atau sumber lain.
- Poin tidak bisa diuangkan (hanya untuk tukar reward).

### A.3 Penarikan Saldo
- **Minimal penarikan**: Rp50.000.
- **Metode**: Tunai di kantor (tahap awal), transfer/e-wallet (tahap lanjut).
- **Proses**: Manual — nasabah mengajukan via aplikasi → admin setujui → pembayaran dilakukan → admin update status jadi 'selesai' → saldo otomatis berkurang.
- **Validasi**: Saldo nasabah harus >= nominal penarikan.

### A.4 Penukaran Poin
- Nasabah mengajukan tukar poin → admin verifikasi → menyerahkan reward → admin update status 'selesai' → poin otomatis berkurang.
- **Masa berlaku poin**: 1 tahun.

## B. Aturan Setoran & Penjemputan

### B.1 Setor Langsung (di Kantor)
1. Nasabah datang dengan sampah yang sudah dipilah.
2. Petugas periksa jenis dan kondisi.
3. Petugas timbang per jenis sampah.
4. Petugas input data ke aplikasi.
5. Sistem hitung nilai rupiah → saldo bertambah → poin bertambah → stok bertambah.
6. Nasabah terima bukti digital.

### B.2 Penjemputan (via Aplikasi)
1. Nasabah ajukan via aplikasi (jenis, estimasi berat, alamat, jadwal).
2. **Minimal estimasi berat**: 5 kg.
3. Admin menerima → setujui/tolak.
4. Jika disetujui: admin tugaskan petugas → jadwalkan.
5. Petugas datang, timbang, input data.
6. Status berubah: menunggu → disetujui → dijadwalkan → dalam_perjalanan → dijemput → selesai.
7. Jika ditolak: menunggu → ditolak.

### B.3 Status Penjemputan (Lengkap)

| Status | Arti | Transisi ke |
|--------|------|-------------|
| menunggu | Permintaan baru | disetujui / ditolak |
| disetujui | Admin setuju | dijadwalkan |
| dijadwalkan | Petugas ditugaskan | dalam_perjalanan |
| dalam_perjalanan | Petugas menuju lokasi | dijemput |
| dijemput | Sampah diambil | selesai |
| selesai | Transaksi selesai | - |
| ditolak | Permintaan ditolak | - |

> **Catatan**: System constraint — TIDAK ada GPS live tracking. Status diperbarui MANUAL oleh petugas di web admin.

## C. Aturan Stok Gudang

- **Stok Masuk**: Bertambah otomatis setiap ada setoran (dari `DetailSetoran.berat_kg`).
- **Stok Keluar**: Berkurang saat penjualan ke mitra.
- **Stok per Kategori**: Disimpan di `KategoriSampah.stok_terkini_kg`.
- **Penjualan**: Admin mencatat mitra, kategori, berat jual, harga jual → sistem kurangi stok.

## D. Aturan Reward

| Reward | Poin Dibutuhkan |
|--------|-----------------|
| Pulsa Rp10.000 | 100 poin |
| Bibit Tanaman | 50 poin |
| Sembako | 250 poin |
| Alat Kebersihan | 300 poin |

(Daftar dapat diubah oleh admin via endpoint reward)

## E. Aturan Pengaduan

1. Nasabah ajukan pengaduan → status 'terbuka'.
2. Admin terima → catat → tindak lanjuti → beri solusi.
3. Setelah selesai → status 'ditutup'.
4. **Target penyelesaian**: 1-2 hari kerja (sesuai indikator Distrik).
5. Setiap pengaduan memiliki nomor laporan otomatis (ID).

## F. Aturan Jam Layanan

- **Hari**: Senin – Sabtu
- **Jam**: 08.00 – 17.00 WIT (UTC+9)
- **Penjemputan**: Maksimal 2x seminggu per wilayah, pesan minimal H-1.

## G. Aturan Perubahan Harga

- Harga dievaluasi bulanan mengikuti harga pengepul mitra.
- Perubahan ditetapkan admin dan diumumkan minimal 3 hari sebelum berlaku.
- Riwayat perubahan harga tersimpan karena `DetailSetoran.harga_saat_itu` merekam harga saat transaksi.

## H. Aturan Laporan

| Jenis Laporan | Waktu | Isi |
|--------------|-------|-----|
| Harian | Setiap akhir hari | Jumlah transaksi, total setoran, total penarikan |
| Mingguan | Akhir minggu | Rekap mingguan, nasabah baru, tonase per jenis |
| Bulanan | Akhir bulan | Laporan lengkap: nasabah, transaksi, stok, penjualan, keuangan |
| Evaluasi | Per kebutuhan | Analisis program, kendala, rekomendasi |

## I. Ringkasan Aturan Numerik

| Aturan | Nilai |
|--------|-------|
| Minimal setoran per jenis | 1 kg |
| Minimal estimasi penjemputan | 5 kg |
| Minimal penarikan saldo | Rp50.000 |
| Konversi saldo ke poin | 1 poin per Rp1.000 |
| Konversi poin ke reward | 100 poin ≈ Rp10.000 |
| Masa berlaku poin | 1 tahun |
| Target penyelesaian pengaduan | 1-2 hari kerja |
| Frekuensi penjemputan | Max 2x/minggu/wilayah |

---

## J. Standar Waktu Pelayanan (dari SOP)

| Layanan | Standar Waktu |
|---------|---------------|
| Verifikasi pendaftaran nasabah | **Maksimal 1 hari kerja** |
| Input transaksi setoran langsung | **Pada hari yang sama** |
| Konfirmasi penjemputan | **Maksimal 1 hari kerja** |
| Penyelesaian penjemputan | **Sesuai jadwal yang disetujui** |
| Penarikan saldo | **Maksimal 1–2 hari kerja** |
| Penanganan pengaduan ringan | **Maksimal 2 hari kerja** |
| Laporan bulanan | **Akhir bulan berjalan** |

> **Target**: 100% pengaduan ditindaklanjuti (sesuai indikator kinerja Distrik Mimika Baru)

---

## K. Indikator Keberhasilan Program (dari SOP)

| Indikator | Target |
|-----------|--------|
| Jumlah nasabah aktif | **Meningkat setiap bulan** |
| Total sampah terkumpul | **Meningkat setiap bulan** |
| Jumlah penjemputan selesai | **Meningkat sesuai permintaan** |
| Jumlah RT/RW aktif | **Bertambah secara bertahap** |
| Nilai ekonomi sampah | **Meningkat setiap bulan** |
| Pengaduan terselesaikan | **Minimal 90% selesai** |
| Laporan bulanan | **Tersedia tepat waktu** |

Indikator ini digunakan oleh Koordinator Program dan Pemerintah Distrik untuk:
- Monitoring dashboard
- Evaluasi program bulanan/tahunan
- Pengambilan keputusan berbasis data

---

## L. Standar Etika Petugas (dari SOP)

1. Melayani masyarakat dengan **sopan, ramah, dan profesional**
2. Menimbang sampah secara **jujur dan transparan**
3. **Tidak melakukan pungutan** di luar ketentuan
4. **Menjaga kerahasiaan** data nasabah
5. Menggunakan akun aplikasi **sesuai kewenangan**
6. **Menjaga kebersihan** lokasi bank sampah
7. **Melaporkan kendala** kepada admin atau koordinator

---

## M. Aturan Penjemputan Wilayah

- **Tahap awal**: Terbatas pada kelurahan sekitar kantor Distrik Mimika Baru
- **Perluasan**: Dilakukan secara bertahap
- **Frekuensi**: Maksimal 2x seminggu per wilayah
- **Pemesanan**: Minimal H-1 sebelum jadwal
- **Minimal berat**: 5 kg total estimasi

---

## N. Aturan Arsip & Retensi Data

- Arsip digital transaksi: **minimal 5 tahun**
- Rekap bulanan: Dicetak dan diarsipkan di kantor distrik (tata kelola arsip OPD)
- Backup database: Otomatis **harian**
- Backup full: **Mingguan**, retensi 30 hari
- Backup disimpan **terpisah** dari server utama

---

## O. Aturan Perubahan Data & Koreksi

- **Koreksi data transaksi**: Hanya oleh admin (bukan petugas biasa)
- **Setiap koreksi tercatat** di audit log dengan informasi:
  - User yang melakukan koreksi
  - Data sebelum dan sesudah
  - Timestamp
- **Penghapusan data**: Tidak diperbolehkan untuk transaksi yang sudah diverifikasi

---

## Referensi Data Lengkap

Untuk data referensi lengkap (harga sampah per kategori, katalog reward, contoh perhitungan, format laporan, jenis pengaduan, kontak organisasi, dll), lihat:
> **`09-data-dictionary.md`** — Data dictionary & reference values
