# MIRU Bank Sampah (Miru-G) — Ekosistem Aplikasi

Sistem digital **Aplikasi Inovasi Bank Sampah Distrik Mimika Baru "MIRU BANK SAMPAH" (Miru-G)** terdiri dari **tiga repositori GitHub terpisah** yang saling terintegrasi melalui REST API.

> **"Sampah Bernilai, Lingkungan Bersih, Warga Sejahtera"**

## Arsitektur Sistem

```
┌─────────────────────┐     ┌─────────────────────┐
│   mirumobileapp     │     │   miru-web-admin    │
│   Flutter (Android) │     │   Next.js + TS      │
│   Role: Nasabah     │     │   Role: Staff       │
└──────────┬──────────┘     └──────────┬──────────┘
           │    JWT + JSON Envelope     │
           └────────────┬───────────────┘
                        ▼
              ┌─────────────────────┐
              │  miru-backend-api   │
              │  Django REST API    │
              │  PostgreSQL/SQLite  │
              └─────────────────────┘
```

## Repositori GitHub

| Repositori | Platform | Teknologi | Target Pengguna | Status |
|------------|----------|-----------|-----------------|--------|
| **miru-backend-api** | REST API | Django 5.2 + DRF + JWT | Semua role (via API) | ✅ Paling maju |
| **miru-web-admin** | Web App | Next.js 16 + TypeScript + Tailwind v4 | Admin, Petugas, Koordinator, Pemerintah Distrik | 🔲 Belum dikerjakan |
| **mirumobileapp** | Mobile App | Flutter 3.x + Dart | Nasabah/Masyarakat | 🔲 Belum dikerjakan |

> Clone masing-masing repositori secara terpisah. Dokumentasi lengkap ada di `README.md` dan `.ai-steering/` **di dalam repo masing-masing**.

## 6 Role Pengguna

| Role | Aplikasi | Deskripsi Singkat |
|------|----------|-------------------|
| **Nasabah** | mirumobileapp | Daftar, setor/jemput, cek saldo, tarik saldo, tukar poin |
| **Petugas** | miru-web-admin | Input setoran, timbang, verifikasi, penjemputan |
| **Admin** | miru-web-admin | Manajemen penuh: nasabah, harga, transaksi, stok, mitra, laporan |
| **Koordinator** | miru-web-admin | Dashboard monitoring, laporan, pengawasan (read-heavy) |
| **Pemerintah Distrik** | miru-web-admin | Laporan & evaluasi program (read-only) |
| **Mitra/Pengepul** | — | Dicatat admin, **tidak punya login** |

## Standarisasi Lintas Repositori

Semua klien frontend **wajib** mengikuti kontrak API **miru-backend-api**:

| Aspek | Standar | Dokumen Sumber |
|-------|---------|----------------|
| Base URL dev | `http://localhost:8000` | **miru-backend-api** — `README.md` |
| Auth | JWT via `/api/auth/login/`, `/api/auth/refresh/`, `/api/auth/me/` | **miru-backend-api** — `.ai-steering/04-api-contracts-and-standards.md` |
| Format response | JSON Envelope (`success`, `status_code`, `message`, `data`, `meta`) | §3 dokumen di atas |
| Penamaan URL | Bahasa Inggris, kebab-case, plural | `/api/waste-categories/`, `/api/deposits/`, dll. |
| Penamaan field | `snake_case` | Sesuai serializer Django |
| Timestamp | ISO 8601 WIT (`+09:00`) | `Asia/Jayapura` |
| Pagination | `?page=1&page_size=20` (max 100) | `meta.pagination` |
| Bahasa UI | Bahasa Indonesia | Semua proyek |

## Urutan Pengembangan

1. **miru-backend-api** — fondasi (sedang berjalan, Fase 1 selesai)
2. **miru-web-admin** — operasional petugas & admin (prioritas kedua)
3. **mirumobileapp** — nasabah (prioritas ketiga)
4. **iOS** — menyusul post-MVP

## Quick Start (Development Lokal)

Jalankan di **masing-masing repositori** (clone terpisah):

```bash
# 1. miru-backend-api
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data --minimal --flush
python manage.py runserver

# 2. miru-web-admin (terminal baru)
cp .env.example .env.local
npm install && npm run dev

# 3. mirumobileapp (terminal baru)
flutter pub get
flutter run
```

## Referensi API Live (saat backend berjalan)

| Resource | URL |
|----------|-----|
| Swagger UI | http://localhost:8000/api/docs/ |
| Panduan Alur per Role | http://localhost:8000/api/guide/ |
| Health Check | http://localhost:8000/health/ |

## Kontak & Instansi

| Item | Detail |
|------|--------|
| Instansi | Kantor Distrik Mimika Baru, Kab. Mimika, Papua Tengah |
| Developer | PT Webekspres Teknologi Indonesia |
| Jam Operasional | Senin–Sabtu, 08.00–17.00 WIT |
