# 01 — Project Overview: MIRU Bank Sampah (Miru-G)

## Latar Belakang

Distrik Mimika Baru, Kabupaten Mimika, Papua Tengah, membutuhkan sistem digital untuk mengelola Bank Sampah yang lebih tertib, transparan, terukur, dan mudah dipantau. Program **Aplikasi Inovasi Bank Sampah Distrik Mimika Baru "MIRU BANK SAMPAH" (Miru-G)** hadir sebagai solusi digital dengan semangat:

> **"Sampah Bernilai, Lingkungan Bersih, Warga Sejahtera"**

Slogan ini selaras dengan motto Distrik Mimika Baru: *"Melayani Dengan Hati — Cepat, Tepat, Transparan & Akuntabel".*

## Tujuan Sistem

1. Menyediakan aplikasi mobile untuk masyarakat mendaftar, cek saldo, ajukan penjemputan, tarik saldo, tukar poin.
2. Mempermudah petugas dalam menerima, menimbang, dan mencatat sampah.
3. Membantu admin mengelola data nasabah, kategori sampah, harga, transaksi, stok, mitra, dan laporan.
4. Meningkatkan transparansi pencatatan transaksi dan saldo nasabah.
5. Mendukung pengelolaan stok gudang dan penjualan ke mitra/pengepul.
6. Menyediakan laporan operasional untuk monitoring dan evaluasi oleh Pemerintah Distrik.
7. Mendukung peningkatan partisipasi masyarakat dalam kebersihan lingkungan.

## 6 Role Pengguna

| No | Role | Deskripsi | Hak Akses Utama |
|----|------|-----------|-----------------|
| 1 | **Nasabah** | Masyarakat pengguna aplikasi mobile | Daftar, setor/jemput sampah, cek saldo, tarik saldo, tukar poin, lihat riwayat, pengaduan |
| 2 | **Petugas Bank Sampah** | Pelaksana lapangan (Web Admin) | Input setoran, timbang sampah, verifikasi, penjemputan, laporan harian |
| 3 | **Admin Aplikasi** | Pengelola utama sistem (Web Admin) | Manajemen nasabah, harga, transaksi, stok, mitra, pengaduan, laporan, audit log |
| 4 | **Koordinator Program** | Pengawas program (Web Admin) | Dashboard monitoring, akses laporan, pengawasan operasional |
| 5 | **Pemerintah Distrik** | Pembina & evaluator (Web Admin) | Akses laporan, evaluasi program, pengambilan keputusan |
| 6 | **Mitra/Pengepul** | Pembeli sampah (data by Admin) | Dicatat sebagai mitra dalam transaksi penjualan (tidak punya akses login langsung) |

## 3 Repositori Sistem

| Repositori | Platform | Teknologi | Target Pengguna |
|------------|----------|-----------|-----------------|
| `miru-backend-api` | REST API | Django + DRF + PostgreSQL | Semua role (via API) |
| `miru-web-admin` | Web App | Next.js + TypeScript + Tailwind | Admin, Petugas, Koordinator, Distrik |
| `mirumobileapp` | Mobile App | Flutter + Dart | Nasabah/Masyarakat |

## Prioritas Pengerjaan

1. **Backend API (Django)** — Fondasi sistem, dikerjakan pertama
2. **Web Admin (Next.js)** — Panel pengelola, prioritas kedua
3. **Mobile App (Flutter)** — Aplikasi nasabah, prioritas ketiga
4. **iOS App** — Paling akhir, menyusul (tidak urgent untuk Mimika)

## Informasi Kontak & Organisasi

| Item | Detail |
|------|--------|
| Penanggung Jawab | Merlyn Temorubun, S,STP (Kepala Distrik Mimika Baru) |
| Koordinator Program | Arfan |
| Admin Sistem | Harorld Sopacua |
| Developer | PT Webekspres Teknologi Indonesia (NIB: 0310240053735) |
| Developer Web | webekspres.id |
| Kontak | WA: 0821 977 3693 |
| Email Instansi | distrikmiru@mimikakab.go.id |
| Email Layanan | distrikmiru72@gmail.com |
| Alamat | Jl. Cendrawasih Poros SP.II, Timika, Papua Tengah 99910 |

## Informasi Aplikasi

| Item | Detail |
|------|--------|
| Nama Lengkap | Aplikasi Inovasi Bank Sampah Distrik Mimika Baru **"MIRU BANK SAMPAH" (Miru-G)** |
| Nama Pendek | MIRU Bank Sampah (Miru-G) |
| Slogan | "Sampah Bernilai, Lingkungan Bersih, Warga Sejahtera" |
| Motto Distrik | "Melayani Dengan Hati — Cepat, Tepat, Transparan & Akuntabel" |
| Deskripsi | Aplikasi bank sampah Distrik Mimika Baru — setor sampah, dapat saldo & poin |
| Logo | Belum ada — akan dibuat oleh Webekspres/pengelola |
| Domain (usulan) | mirubanksampah.id / miru-g.id / subdomain pemda |
| Server | Layanan dari Webekspres (klien belum punya server) |
| SSL | **WAJIB** HTTPS untuk seluruh akses sistem |

## Jam Layanan Operasional

| Hari | Jam | Zona Waktu |
|------|-----|-----------|
| Senin – Sabtu | **08.00 – 17.00** | **WIT** (UTC+9) |
| Minggu & Hari Libur | **Libur** | - |

## Indikator Keberhasilan Program

Sistem dikembangkan untuk mendukung pencapaian indikator berikut (sumber: SOP):

| Indikator | Target |
|-----------|--------|
| Jumlah nasabah aktif | Meningkat setiap bulan |
| Total sampah terkumpul | Meningkat setiap bulan |
| Jumlah penjemputan selesai | Meningkat sesuai permintaan |
| Jumlah RT/RW aktif | Bertambah secara bertahap |
| Nilai ekonomi sampah | Meningkat setiap bulan |
| Pengaduan terselesaikan | Minimal 90% selesai |
| Laporan bulanan | Tersedia tepat waktu |

## Standar Pelayanan

| Layanan | Target Waktu |
|---------|-------------|
| Verifikasi pendaftaran | Maksimal 1 hari kerja |
| Input transaksi setoran | Hari yang sama |
| Konfirmasi penjemputan | Maksimal 1 hari kerja |
| Penarikan saldo | Maksimal 1–2 hari kerja |
| Penanganan pengaduan | Maksimal 2 hari kerja |

## Referensi Data Lengkap

Untuk data referensi lengkap (harga sampah per kategori, katalog reward, contoh perhitungan, format laporan, jenis pengaduan, standar etika, dll), lihat:
> **`09-data-dictionary.md`** — Data dictionary & reference values
