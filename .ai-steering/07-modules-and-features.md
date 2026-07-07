# 07 — Modules & Features (Backend)

## 17 Modul Sistem — Peran Backend

| No | Modul | Backend (Django) | Web Admin (Next.js) | Mobile (Flutter) |
|----|-------|------------------|--------------------|-----------------|
| 1 | Manajemen Akses & Pengguna | ✅ User CRUD, Role management | ✅ Full CRUD UI | ❌ (tidak ada) |
| 2 | Autentikasi & Akun Nasabah | ✅ JWT Auth, Register, Login | ✅ (untuk staff) | ✅ Login, Register |
| 3 | Profil & Kartu Digital | ✅ User detail, QR data API | ✅ View nasabah | ✅ Profil, QR card |
| 4 | Informasi & Edukasi Sampah | ✅ Kategori CRUD | ✅ Kelola konten | ✅ Lihat info |
| 5 | Katalog & Harga Sampah | ✅ CRUD harga, history | ✅ Kelola harga | ✅ Lihat harga |
| 6 | Setor Sampah Langsung | ✅ Transaksi + Detail + Side effects | ✅ Input setoran | ❌ |
| 7 | Penjemputan Sampah | ✅ CRUD + Status workflow | ✅ Kelola penjemputan | ✅ Ajukan, cek status |
| 8 | Penimbangan & Verifikasi | ✅ Bagian dari TransaksiSetoran | ✅ Input timbang | ❌ |
| 9 | Saldo & Riwayat Transaksi | ✅ Filter transaksi per user | ✅ Riwayat all user | ✅ Riwayat sendiri |
| 10 | Penarikan Saldo | ✅ CRUD + Validasi | ✅ Proses penarikan | ✅ Ajukan tarik |
| 11 | Poin & Reward | ✅ Reward CRUD, Penukaran | ✅ Kelola reward | ✅ Tukar poin |
| 12 | Stok Gudang | ✅ Stok otomatis dari setoran/jual | ✅ Monitor stok | ❌ |
| 13 | Penjualan ke Mitra | ✅ Penjualan CRUD | ✅ Catat penjualan | ❌ |
| 14 | Pengaduan Nasabah | ✅ CRUD + Status | ✅ Kelola pengaduan | ✅ Ajukan pengaduan |
| 15 | Dashboard & Monitoring | ✅ Aggregated data API | ✅ Dashboard UI | ❌ |
| 16 | Laporan & Ekspor Data | ✅ Laporan endpoint | ✅ Tabel + ekspor Excel | ❌ |
| 17 | Pengaturan Sistem & Audit Log | ✅ Config API | ✅ Pengaturan | ❌ |

## Detail Endpoint Backend per Modul

### Modul 1: Manajemen Akses & Pengguna
- `GET/POST/PATCH/DELETE /api/users/` — CRUD user
- Filter: `?role=nasabah&is_active=true`
- Search: `?search=nama`

### Modul 2: Autentikasi & Akun Nasabah
- `POST /api/token/` — Login
- `POST /api/token/refresh/` — Refresh token
- `POST /api/users/` — Registrasi (dengan role=nasabah default)

### Modul 3: Profil & Kartu Digital
- `GET /api/users/{id}/` — Profil lengkap
- `PATCH /api/users/{id}/` — Update profil
- Data untuk QR code: `{id, nama_lengkap, no_hp}` — di-encode di frontend

### Modul 4-5: Kategori & Harga Sampah
- `GET/POST/PATCH/DELETE /api/waste-categories/`
- Kategori default: Plastik PET, Gelas Plastik, Kardus, Kertas Putih, Aluminium, Besi, Kaca, Minyak Jelantah

### Modul 6: Setor Sampah Langsung
- `POST /api/deposits/` — Create dengan nested details
- Side effects:
  - Hitung total_nilai dari details.
  - Update saldo nasabah (+total_nilai).
  - Update poin nasabah (+int(total_nilai/1000)).
  - Update stok kategori (+berat_kg per detail).

### Modul 7: Penjemputan Sampah
- `POST /api/pickups/` — Ajukan (nasabah)
- `PATCH /api/pickups/{id}/` — Update status (petugas/admin)
- Filter by status: `?status=menunggu`

### Modul 8: Penimbangan & Verifikasi
- Bagian dari Modul 6 (setoran).
- Petugas input kategori + berat → sistem hitung subtotal otomatis.

### Modul 9: Saldo & Riwayat
- `GET /api/deposits/?nasabah={id}` — Riwayat setoran
- `GET /api/withdrawals/?nasabah={id}` — Riwayat penarikan
- `GET /api/reward-redemptions/?nasabah={id}` — Riwayat penukaran poin

### Modul 10: Penarikan Saldo
- `POST /api/withdrawals/` — Ajukan (validasi: nominal >= 50000, saldo >= nominal)
- `PATCH /api/withdrawals/{id}/` — Admin setujui (status → 'selesai', kurangi saldo)
- Filter: `?status=menunggu`

### Modul 11: Poin & Reward
- `GET/POST/PATCH/DELETE /api/rewards/` — CRUD reward
- `POST /api/reward-redemptions/` — Tukar poin (validasi: poin >= reward.poin_dibutuhkan)
- `PATCH /api/reward-redemptions/{id}/` — Admin setujui

### Modul 12: Stok Gudang
- `GET /api/waste-categories/` — Lihat stok per kategori (stok_terkini_kg)
- Update otomatis via transaksi setoran (+stok) dan penjualan mitra (-stok)

### Modul 13: Penjualan ke Mitra
- `POST /api/partner-sales/` — Catat penjualan (kurangi stok otomatis)
- `POST /api/partners/` — CRUD mitra

### Modul 14: Pengaduan
- `POST /api/complaints/` — Ajukan (nasabah)
- `GET /api/complaints/` — List (nasabah lihat sendiri, admin lihat semua)
- `PATCH /api/complaints/{id}/` — Admin update tindak lanjut & status

### Modul 15: Dashboard & Monitoring
- Data agregat yang perlu disediakan:
  - Total nasabah, nasabah aktif (bertransaksi dalam 30 hari)
  - Total sampah terkumpul (per periode)
  - Total penjemputan (per status)
  - Total penarikan & penukaran poin (per periode)
  - Stok terkini per kategori

### Modul 16: Laporan & Ekspor
- Endpoint khusus untuk data laporan:
  - `GET /api/reports/daily/?tanggal=2026-07-03`
  - `GET /api/reports/monthly/?bulan=7&tahun=2026`
- Ekspor bisa dilakukan di frontend (download CSV/Excel dari data JSON)

### Modul 17: Pengaturan Sistem & Audit Log
- Pengaturan profil institusi (nama, logo URL, kontak, pengumuman)
- Audit log: setiap perubahan data penting dicatat dengan user, aksi, timestamp
