# 06 — System Constraints (Batasan Sistem)

## ⚠️ BATASAN KERAS — INI TIDAK BOLEH DIIMPLEMENTASIKAN

### 1. TIDAK ADA Integrasi Payment Gateway Otomatis
- **Larangan**: Jangan integrasikan Midtrans, Xendit, Stripe, atau payment gateway apapun.
- **Yang benar**: Pencairan saldo dilakukan **MANUAL** oleh admin.
- Alur: Nasabah mengajukan penarikan → admin setujui → admin bayar tunai/transfer → admin update status.
- API hanya mencatat pengajuan dan mengubah status, tidak memproses pembayaran.

### 2. TIDAK ADA GPS Live Tracking
- **Larangan**: Jangan implementasikan real-time GPS tracking untuk armada penjemputan.
- **Yang benar**: Status penjemputan diperbarui **MANUAL** oleh petugas via web admin.
- Status: menunggu → disetujui → dijadwalkan → dalam_perjalanan → dijemput → selesai.

### 3. TIDAK ADA Integrasi Hardware Fisik
- **Larangan**: Jangan integrasikan timbangan digital otomatis, barcode scanner fisik, atau printer struk.
- **Yang benar**: Berat diinput manual oleh petugas. Scanner menggunakan kamera HP (QR code).
- Bukti transaksi digital (PDF/gambar), bukan cetak struk fisik.

### 4. TIDAK ADA Integrasi Dukcapil
- **Larangan**: Jangan integrasikan API Dukcapil untuk validasi NIK.
- NIK hanya data opsional, tidak divalidasi ke database kependudukan.

### 5. Google Maps API — Sederhana Saja
- Integrasi peta hanya untuk menampilkan alamat penjemputan (static map atau input alamat).
- **Jangan implementasikan** navigasi real-time, distance matrix, atau geofencing.
- Biaya API peta menjadi tanggung jawab klien.

### 6. Keamanan & Privasi
- Data nasabah (nama, alamat, no HP) hanya untuk operasional bank sampah.
- NIK/foto KTP hanya untuk verifikasi penarikan saldo besar.
- Data disimpan terenkripsi, tidak dibagikan ke pihak ketiga.
- Tunduk pada UU No. 27/2022 tentang Perlindungan Data Pribadi.

### 7. Backup & Maintenance
- Backup otomatis harian (database) dan mingguan (full).
- Retensi minimal 30 hari.
- Maintenance fix bug & update minor sesuai periode layanan.

### 8. Arsip Transaksi
- Arsip digital minimal 5 tahun.
- Rekap bulanan dicetak dan diarsipkan di kantor distrik.

### 9. Batasan Multi-Tenant
- Sistem ini untuk **satu** Bank Sampah (Distrik Mimika Baru), **bukan** platform multi-tenant.
- Jangan desain untuk banyak bank sampah independen.

### 10. Publikasi Aplikasi
- Android: Prioritas utama, publikasi via Google Play Store.
- iOS: Menyusul kemudian (belum urgent).
- Akun developer (Google Play Console, Apple Developer) disediakan oleh klien.

### 11. Batasan Role
- Mitra/Pengepul **tidak login ke sistem**. Data mitra dikelola oleh admin.
- Pemerintah Distrik hanya punya akses **baca** (laporan dan dashboard).
- Nasabah hanya bisa akses data milik sendiri (kecuali admin).

### 12. Batasan Teknis Backend
- Framework Django 5.2 — periksa compatibility sebelum install library baru.
- Database PostgreSQL 15 — gunakan fitur yang didukung.
- JWT token expire 24 jam — jangan implementasikan refresh token otomatis tanpa expiry.
- Gunakan SQLite untuk development lokal (set `USE_POSTGRES=False`).
