# 04 — API Contracts & Standards

## Base URL

- Development: `http://localhost:8000/api/`
- Production: `https://api.mirubanksampah.id/api/`

## Autentikasi — JWT (simplejwt)

Semua endpoint (kecuali registrasi dan list kategori) memerlukan JWT token.

### Endpoint Auth

```
POST /api/token/          # Login — dapatkan access + refresh token
POST /api/token/refresh/  # Refresh access token
```

### Request Login
```json
{
  "username": "string",
  "password": "string"
}
```

### Response Login
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Format Header
```
Authorization: Bearer <access_token>
```

### Claim JWT
- `user_id`: ID user
- `role`: role user ('nasabah', 'petugas', 'admin', 'koordinator')
- `exp`: expiration time (default 24 jam)

## Standar Response Format

### Success Response (List)
```json
{
  "count": 50,
  "next": "http://api.example.com/api/users/?page=3",
  "previous": null,
  "results": [
    { ... }
  ]
}
```

### Success Response (Detail)
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2"
}
```

### Error Response (Validation)
```json
{
  "field_name": ["Error message 1", "Error message 2"]
}
```

### Error Response (General)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## API Endpoints Lengkap

### 1. Users (Manajemen Pengguna)
| Method | Endpoint | Permission | Deskripsi |
|--------|----------|------------|-----------|
| POST | `/api/users/` | AllowAny | Registrasi nasabah baru |
| GET | `/api/users/` | Admin/Koordinator | List semua user |
| GET | `/api/users/{id}/` | Owner/Admin | Detail user |
| PATCH | `/api/users/{id}/` | Owner/Admin | Update profil user |
| DELETE | `/api/users/{id}/` | Admin/Koordinator | Hapus user |

**POST /api/users/ (Registrasi)**
```json
{
  "username": "string (required)",
  "password": "string (required, min 6 chars)",
  "nama_lengkap": "string (required)",
  "nik": "string (16 digit, optional)",
  "no_hp": "string (optional)",
  "alamat": "string (optional)",
  "role": "nasabah (default)"
}
```

**Response Registrasi:**
```json
{
  "id": 1,
  "username": "nasabah1",
  "role": "nasabah",
  "nama_lengkap": "Budi Santoso",
  "nik": "1234567890123456",
  "no_hp": "08123456789",
  "alamat": "Jl. Contoh No. 1",
  "saldo": 0,
  "poin": 0
}
```

### 2. Kategori Sampah
| Method | Endpoint | Permission | Deskripsi |
|--------|----------|------------|-----------|
| GET | `/api/sampah/kategori/` | AllowAny | List semua kategori |
| GET | `/api/sampah/kategori/{id}/` | AllowAny | Detail kategori |
| POST | `/api/sampah/kategori/` | Admin/Koordinator | Tambah kategori |
| PATCH | `/api/sampah/kategori/{id}/` | Admin/Koordinator | Update kategori |
| DELETE | `/api/sampah/kategori/{id}/` | Admin/Koordinator | Hapus kategori |

```json
// GET /api/sampah/kategori/
[
  {
    "id": 1,
    "nama": "Plastik PET",
    "harga_beli_per_kg": 3000.00,
    "stok_terkini_kg": 150.50
  },
  ...
]
```

### 3. Transaksi Setoran
| Method | Endpoint | Permission | Deskripsi |
|--------|----------|------------|-----------|
| GET | `/api/transaksi/` | Owner/Admin | List transaksi |
| GET | `/api/transaksi/{id}/` | Owner/Admin | Detail transaksi + details |
| POST | `/api/transaksi/` | Petugas/Admin | Input setoran baru |

**POST /api/transaksi/**
```json
{
  "nasabah": 1,
  "petugas": 2,
  "details": [
    {
      "kategori": 1,
      "berat_kg": 5.00,
      "harga_saat_itu": 3000.00,
      "subtotal": 15000.00
    },
    {
      "kategori": 2,
      "berat_kg": 3.00,
      "harga_saat_itu": 1500.00,
      "subtotal": 4500.00
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "nasabah": 1,
  "petugas": 2,
  "tanggal": "2026-07-03T10:30:00Z",
  "total_nilai": 19500.00,
  "status": "selesai",
  "details": [
    {
      "id": 1,
      "kategori": 1,
      "berat_kg": 5.00,
      "harga_saat_itu": 3000.00,
      "subtotal": 15000.00
    },
    {
      "id": 2,
      "kategori": 2,
      "berat_kg": 3.00,
      "harga_saat_itu": 1500.00,
      "subtotal": 4500.00
    }
  ]
}
```

**Side Effects (done automatis):**
- Tambah saldo nasabah sebesar `total_nilai`
- Tambah poin nasabah: `int(total_nilai / 1000)` (1 poin per Rp1.000)
- Tambah stok_terkini_kg di KategoriSampah

### 4. Penjemputan
| Method | Endpoint | Permission | Deskripsi |
|--------|----------|------------|-----------|
| POST | `/api/penjemputan/` | Nasabah/Owner | Ajukan penjemputan |
| GET | `/api/penjemputan/` | Owner/Admin | List penjemputan |
| GET | `/api/penjemputan/{id}/` | Owner/Admin | Detail penjemputan |
| PATCH | `/api/penjemputan/{id}/` | Petugas/Admin | Update status |

**Filter:** `?nasabah=1&status=menunggu`

### 5. Penarikan Saldo
| Method | Endpoint | Permission | Deskripsi |
|--------|----------|------------|-----------|
| POST | `/api/saldo/` | Nasabah | Ajukan penarikan |
| GET | `/api/saldo/` | Owner/Admin | List penarikan |
| PATCH | `/api/saldo/{id}/` | Admin | Setujui/tolak penarikan |

**Constraint:** nominal >= 50000, saldo nasabah >= nominal

### 6. Reward
| Method | Endpoint | Permission | Deskripsi |
|--------|----------|------------|-----------|
| GET | `/api/reward/katalog/` | AllowAny | List reward |
| POST | `/api/reward/katalog/` | Admin | Tambah reward |
| PATCH | `/api/reward/katalog/{id}/` | Admin | Update reward |

### 7. Penukaran Poin
| Method | Endpoint | Permission | Deskripsi |
|--------|----------|------------|-----------|
| POST | `/api/reward/tukar/` | Nasabah | Ajukan tukar poin |
| GET | `/api/reward/tukar/` | Owner/Admin | List penukaran |
| PATCH | `/api/reward/tukar/{id}/` | Admin | Setujui penukaran |

### 8. Mitra Pengepul
| Method | Endpoint | Permission | Deskripsi |
|--------|----------|------------|-----------|
| GET | `/api/gudang/mitra/` | Admin/Koordinator | List mitra |
| POST | `/api/gudang/mitra/` | Admin | Tambah mitra |

### 9. Penjualan Mitra
| Method | Endpoint | Permission | Deskripsi |
|--------|----------|------------|-----------|
| POST | `/api/gudang/jual/` | Admin | Catat penjualan ke mitra |
| GET | `/api/gudang/jual/` | Admin/Koordinator | List penjualan |

### 10. Pengaduan
| Method | Endpoint | Permission | Deskripsi |
|--------|----------|------------|-----------|
| POST | `/api/pengaduan/` | Nasabah | Ajukan pengaduan |
| GET | `/api/pengaduan/` | Owner/Admin | List pengaduan |
| PATCH | `/api/pengaduan/{id}/` | Admin | Update status/tindak lanjut |

## Filtering (django-filter)

Semua list endpoint mendukung filtering via query parameters:
```
GET /api/transaksi/?nasabah=1
GET /api/penjemputan/?status=menunggu
GET /api/users/?role=nasabah
GET /api/pengaduan/?status=terbuka
```

## Pagination

- Default: PageNumberPagination, 20 items per page
- Kustom: `?page=1&page_size=50` (max page_size = 100)

## Rate Limiting (Future)

Belum diimplementasikan — akan ditambahkan di tahap post-MVP jika diperlukan.

## Versioning

API menggunakan URL prefix `/api/`. Saat ini versi 1 (tidak ada prefix v1). Jika ada breaking changes di masa depan, akan ditambahkan prefix `/api/v2/`.
