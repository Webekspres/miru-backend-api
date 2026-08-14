# 04 — API Contracts & Standards

> **Dokumen ini** mendefinisikan kontrak API backend MIRU Bank Sampah:
> format request/response standar industri, kode HTTP, autentikasi, dan spesifikasi endpoint lengkap.
>
> **Base URL:**
> - Development: `http://localhost:8000`
> - Production: `https://api.mirubanksampah.id` (usulan)

---

## 1. Prinsip Desain API

| Prinsip | Implementasi |
|---------|--------------|
| Arsitektur | REST over HTTP/JSON |
| Format data | `application/json` (UTF-8) |
| Penamaan field | `snake_case` (konvensi Django/Python) |
| Penamaan URL | `kebab-case` untuk path multi-kata |
| Timestamp | ISO 8601 dengan timezone: `2026-07-07T14:30:00+09:00` |
| Mata uang | `Decimal` sebagai string JSON: `"50000.00"` |
| Berat | Kilogram (`kg`), 2 desimal: `"5.50"` |
| Idempotensi | Operasi approve/reject harus aman dari double-submit |
| Versioning | Prefix `/api/` (v1 implisit); `/api/v2/` jika breaking change |

### 1.1 Route Naming (English, kebab-case)

Semua URL API menggunakan **bahasa Inggris**, plural nouns, kebab-case.

| Resource | Route | Deskripsi |
|----------|-------|-----------|
| Users | `/api/users/` | Manajemen pengguna |
| Waste categories | `/api/waste-categories/` | Kategori & harga sampah |
| Deposits | `/api/deposits/` | Transaksi setoran |
| Pickups | `/api/pickups/` | Penjemputan sampah |
| Withdrawals | `/api/withdrawals/` | Penarikan saldo |
| Rewards | `/api/rewards/` | Katalog reward |
| Reward redemptions | `/api/reward-redemptions/` | Penukaran poin |
| Partners | `/api/partners/` | Mitra pengepul |
| Partner sales | `/api/partner-sales/` | Penjualan ke mitra |
| Inventory | `/api/inventory/` | Stok gudang (planned) |
| Complaints | `/api/complaints/` | Pengaduan nasabah |
| Activity | `/api/activity/` | Riwayat gabungan (planned) |
| Dashboard | `/api/dashboard/` | Monitoring (planned) |
| Reports | `/api/reports/` | Laporan (planned) |
| Settings | `/api/settings/` | Pengaturan institusi (planned) |
| Auth | `/api/auth/login/`, `/api/auth/refresh/`, `/api/auth/me/` | Autentikasi |

---

## 2. Autentikasi — JWT (RFC 7519)

Semua endpoint memerlukan JWT **kecuali** yang ditandai `Public`.

### 2.1 Login

```
POST /api/auth/login/
Content-Type: application/json
```

**Request:**
```json
{
  "username": "nasabah1",
  "password": "password123"
}
```

**Response `200 OK`:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Login berhasil.",
  "data": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "nasabah1",
      "role": "nasabah",
      "nama_lengkap": "Budi Santoso"
    }
  },
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc123"
  }
}
```

**Response `401 Unauthorized`:**
```json
{
  "success": false,
  "status_code": 401,
  "message": "Username atau password salah.",
  "code": "AUTHENTICATION_FAILED",
  "data": null,
  "errors": null,
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc124"
  }
}
```

### 2.2 Refresh Token

```
POST /api/auth/refresh/
Content-Type: application/json
```

**Request:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response `200 OK`:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Token berhasil diperbarui.",
  "data": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc125"
  }
}
```

### 2.3 Profil User Login

```
GET /api/auth/me/
Authorization: Bearer <access_token>
```

**Response `200 OK`:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Profil berhasil diambil.",
  "data": {
    "id": 1,
    "username": "nasabah1",
    "role": "nasabah",
    "nama_lengkap": "Budi Santoso",
    "no_hp": "08123456789",
    "alamat": "Jl. Cendrawasih No. 1, Timika",
    "saldo": "125000.00",
    "poin": 125,
    "is_active": true,
    "date_joined": "2026-07-01T08:00:00+09:00"
  },
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc126"
  }
}
```

### 2.4 Header Autentikasi

```
Authorization: Bearer <access_token>
Content-Type: application/json
Accept: application/json
Accept-Language: id
```

### 2.5 JWT Claims

| Claim | Tipe | Deskripsi |
|-------|------|-----------|
| `user_id` | integer | ID user |
| `role` | string | `nasabah`, `petugas`, `admin`, `koordinator`, `pemerintah` |
| `exp` | integer | Unix timestamp expiry (default: 24 jam) |

---

## 3. Format Response Standar Industri — JSON Envelope

API MIRU menggunakan **JSON Envelope** — format response lengkap yang membungkus semua data dalam struktur konsisten. Ini adalah pola standar industri yang dipakai banyak API enterprise, fintech, dan aplikasi pemerintahan di Indonesia.

> **Prinsip ganda:** HTTP status code **tetap dikirim di header** (`200`, `400`, `401`, dll.) **dan** dicerminkan di body (`status_code`). Frontend bisa cek keduanya; `success` boolean memudahkan pengecekan cepat.

### 3.1 Struktur Envelope (Semua Response)

| Field | Tipe | Sukses | Error | Deskripsi |
|-------|------|--------|-------|-----------|
| `success` | boolean | ✅ | ✅ | `true` jika berhasil, `false` jika gagal |
| `status_code` | integer | ✅ | ✅ | HTTP status code (mirror dari header) |
| `message` | string | ✅ | ✅ | Pesan human-readable (Bahasa Indonesia) |
| `data` | object/array/null | ✅ | ✅ | Payload utama; `null` jika error |
| `code` | string | ❌ | ✅ | Kode error machine-readable (hanya saat error) |
| `errors` | object/null | ❌ | ✅ | Detail error per-field (validasi) |
| `meta` | object | ✅ | ✅ | Metadata tambahan (pagination, timestamp, request_id) |

### 3.2 Response Sukses — Resource Tunggal

**`200 OK` — GET / PATCH:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Data berhasil diambil.",
  "data": {
    "id": 1,
    "nama_lengkap": "Budi Santoso",
    "saldo": "125000.00"
  },
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc127"
  }
}
```

**`201 Created` — POST:**
```json
{
  "success": true,
  "status_code": 201,
  "message": "Transaksi setoran berhasil dicatat.",
  "data": {
    "id": 42,
    "status": "selesai",
    "tanggal": "2026-07-07T10:30:00+09:00",
    "total_nilai": "20250.00"
  },
  "meta": {
    "timestamp": "2026-07-07T10:30:00+09:00",
    "request_id": "req_abc128"
  }
}
```

**`204 No Content` — DELETE:**
```json
{
  "success": true,
  "status_code": 204,
  "message": "Data berhasil dihapus.",
  "data": null,
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc129"
  }
}
```

### 3.3 Response Sukses — Koleksi (Paginated)

**`200 OK`:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Daftar transaksi berhasil diambil.",
  "data": [
    {
      "id": 1,
      "nasabah": 5,
      "total_nilai": "19500.00",
      "tanggal": "2026-07-07T10:30:00+09:00",
      "status": "selesai"
    },
    {
      "id": 2,
      "nasabah": 5,
      "total_nilai": "8500.00",
      "tanggal": "2026-07-06T09:15:00+09:00",
      "status": "selesai"
    }
  ],
  "meta": {
    "pagination": {
      "count": 150,
      "page": 1,
      "page_size": 20,
      "total_pages": 8,
      "next": "http://localhost:8000/api/deposits/?page=2",
      "previous": null
    },
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc130"
  }
}
```

**Parameter pagination:**

| Param | Default | Max | Deskripsi |
|-------|---------|-----|-----------|
| `page` | 1 | — | Nomor halaman |
| `page_size` | 20 | 100 | Jumlah item per halaman |

### 3.4 Response Sukses — Aksi Kustom

Untuk endpoint action (approve, reject, assign):

**`200 OK`:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Penjemputan berhasil disetujui.",
  "data": {
    "id": 10,
    "status": "disetujui",
    "updated_at": "2026-07-07T11:00:00+09:00"
  },
  "meta": {
    "timestamp": "2026-07-07T11:00:00+09:00",
    "request_id": "req_abc131"
  }
}
```

### 3.5 Response Error — Format Standar

Semua error mengembalikan envelope yang sama (target implementasi Fase 1):

**Validasi gagal `400`:**
```json
{
  "success": false,
  "status_code": 400,
  "message": "Satu atau lebih field tidak valid.",
  "code": "VALIDATION_ERROR",
  "data": null,
  "errors": {
    "nominal": ["Nominal penarikan minimal Rp50.000."],
    "password": ["Password minimal 6 karakter."]
  },
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc132"
  }
}
```

**Aturan bisnis dilanggar `422`:**
```json
{
  "success": false,
  "status_code": 422,
  "message": "Saldo tidak mencukupi untuk penarikan ini.",
  "code": "INSUFFICIENT_BALANCE",
  "data": null,
  "errors": {
    "nominal": ["Saldo tersedia: Rp45.000,00. Minimal penarikan: Rp50.000,00."]
  },
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc133"
  }
}
```

**Tidak punya akses `403`:**
```json
{
  "success": false,
  "status_code": 403,
  "message": "Anda tidak memiliki izin untuk melakukan aksi ini.",
  "code": "PERMISSION_DENIED",
  "data": null,
  "errors": null,
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc134"
  }
}
```

| Field Error | Tipe | Wajib | Deskripsi |
|-------------|------|-------|-----------|
| `success` | boolean | ✅ | Selalu `false` |
| `status_code` | integer | ✅ | HTTP status code |
| `message` | string | ✅ | Pesan error untuk ditampilkan ke user |
| `code` | string | ✅ | Kode error machine-readable |
| `data` | null | ✅ | Selalu `null` saat error |
| `errors` | object/null | ✅ | Detail per-field; `null` jika bukan validasi |
| `meta` | object | ✅ | `timestamp`, `request_id` |

### 3.6 Kode Error Standar

| HTTP Status | Code | Kapan Digunakan |
|-------------|------|-----------------|
| `400` | `VALIDATION_ERROR` | Input tidak valid |
| `401` | `AUTHENTICATION_FAILED` | Token tidak ada / expired / invalid |
| `403` | `PERMISSION_DENIED` | Role tidak punya akses |
| `404` | `NOT_FOUND` | Resource tidak ditemukan |
| `409` | `CONFLICT` | Transisi status tidak valid / double processing |
| `422` | `BUSINESS_RULE_VIOLATION` | Melanggar aturan bisnis SOP |
| `429` | `RATE_LIMIT_EXCEEDED` | Terlalu banyak request |
| `500` | `INTERNAL_ERROR` | Error server (jangan expose detail di production) |

### 3.7 Kode Error Bisnis (Domain-Specific)

| Code | Pesan | Modul |
|------|-------|-------|
| `MIN_WEIGHT_NOT_MET` | Minimal setoran 1 kg per jenis sampah | Transaksi |
| `MIN_PICKUP_WEIGHT` | Minimal estimasi penjemputan 5 kg | Penjemputan |
| `MIN_WITHDRAWAL_AMOUNT` | Minimal penarikan Rp50.000 | Penarikan |
| `INSUFFICIENT_BALANCE` | Saldo tidak mencukupi | Penarikan |
| `INSUFFICIENT_POINTS` | Poin tidak mencukupi | Penukaran |
| `INSUFFICIENT_STOCK` | Stok tidak mencukupi | Penjualan/Reward |
| `INVALID_STATUS_TRANSITION` | Perubahan status tidak diizinkan | Penjemputan |
| `DUPLICATE_PENDING_REQUEST` | Masih ada pengajuan yang menunggu | Penarikan/Penukaran |
| `ALREADY_PROCESSED` | Pengajuan sudah diproses | Penarikan/Penukaran |
| `SCHEDULE_TOO_SOON` | Jadwal penjemputan minimal H+1 | Penjemputan |
| `OUTSIDE_SERVICE_HOURS` | Di luar jam layanan (08.00–17.00 WIT) | Umum |

### 3.8 Pesan Sukses Standar (Bahasa Indonesia)

| Operasi | Message Default |
|---------|-----------------|
| GET list | `"Daftar {resource} berhasil diambil."` |
| GET detail | `"Data {resource} berhasil diambil."` |
| POST create | `"{Resource} berhasil dibuat."` |
| PATCH update | `"{Resource} berhasil diperbarui."` |
| DELETE | `"{Resource} berhasil dihapus."` |
| Approve | `"{Resource} berhasil disetujui."` |
| Reject | `"{Resource} berhasil ditolak."` |

### 3.9 Implementasi Backend (DRF)

Target Fase 1 — buat custom renderer & exception handler:

```
api/
├── utils/
│   ├── response.py          # helper: success_response(), error_response()
│   ├── pagination.py        # custom pagination → meta.pagination
│   ├── exception_handler.py # wrap semua error ke envelope
│   └── renderers.py         # custom JSON renderer untuk envelope
```

**Contoh helper:**
```python
def success_response(data, message="Berhasil.", status_code=200, meta=None):
    return Response({
        "success": True,
        "status_code": status_code,
        "message": message,
        "data": data,
        "meta": {
            "timestamp": timezone.now().isoformat(),
            "request_id": get_request_id(),
            **(meta or {})
        }
    }, status=status_code)
```

### 3.10 Perbandingan dengan Pola Lain

| Pola | Contoh | Dipakai MIRU? |
|------|--------|---------------|
| **JSON Envelope** | `{ success, status_code, message, data, meta }` | ✅ **Ya — standar MIRU** |
| REST murni | Body = resource langsung, status di header saja | ❌ Tidak |
| RFC 7807 Problem Details | `{ type, title, status, detail }` | ❌ Tidak (diganti envelope) |
| JSON:API | `{ data, included, links }` | ❌ Terlalu kompleks untuk proyek ini |
| GraphQL | Query/mutation terpisah | ❌ Tidak dipakai |

---

## 4. Konvensi HTTP Methods & Status

| Method | Penggunaan | Status Sukses |
|--------|------------|---------------|
| `GET` | Ambil data (idempotent) | `200` |
| `POST` | Buat resource / aksi | `201` (create), `200` (action) |
| `PATCH` | Update sebagian | `200` |
| `PUT` | Replace penuh (hindari, pakai PATCH) | `200` |
| `DELETE` | Hapus (hanya non-transaksi) | `204` |

---

## 5. Filtering, Searching, Ordering

### 5.1 Filtering (django-filter)

```
GET /api/deposits/?nasabah=5&status=selesai
GET /api/pickups/?status=menunggu&petugas=3
GET /api/users/?role=nasabah&is_active=true
GET /api/complaints/?status=terbuka&jenis_pengaduan=saldo_belum_masuk
GET /api/withdrawals/?status=menunggu
```

### 5.2 Date Range Filtering

```
GET /api/deposits/?tanggal_after=2026-07-01&tanggal_before=2026-07-31
GET /api/reports/daily/?tanggal=2026-07-07
GET /api/reports/monthly/?bulan=7&tahun=2026
```

### 5.3 Searching

```
GET /api/users/?search=budi
```

### 5.4 Ordering

```
GET /api/deposits/?ordering=-tanggal
GET /api/pickups/?ordering=status,-jadwal
```

---

## 6. Spesifikasi Endpoint Lengkap

> **Catatan format:** Semua response API menggunakan **JSON Envelope** (lihat §3). Contoh di bawah menampilkan struktur lengkap. Field `meta.timestamp` dan `meta.request_id` selalu ada di setiap response.

### 6.1 Health Check

```
GET /health/
Public
```

**Response `200 OK`:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Server berjalan normal.",
  "data": {
    "status": "ok"
  },
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_health_001"
  }
}
```

**Response production (target Fase 7):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Server berjalan normal.",
  "data": {
    "status": "ok",
    "database": "connected",
    "version": "1.0.0"
  },
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_health_001"
  }
}
```

---

### 6.2 Users — Manajemen Pengguna

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| `POST` | `/api/users/` | Public | Registrasi nasabah |
| `GET` | `/api/users/` | JWT | Admin, Koordinator |
| `GET` | `/api/users/{id}/` | JWT | Owner, Admin, Koordinator |
| `PATCH` | `/api/users/{id}/` | JWT | Owner (profil), Admin |
| `DELETE` | `/api/users/{id}/` | JWT | Admin, Koordinator |

**POST /api/users/ — Registrasi Nasabah**

Request:
```json
{
  "username": "budi_santoso",
  "password": "rahasia123",
    "nama_lengkap": "Budi Santoso",
  "alamat": "Jl. Cendrawasih No. 1, Timika",
  "setuju_kebijakan_data": true
}
```

Response `201 Created`:
```json
{
  "success": true,
  "status_code": 201,
  "message": "Registrasi nasabah berhasil.",
  "data": {
    "id": 15,
    "username": "budi_santoso",
    "role": "nasabah",
    "nama_lengkap": "Budi Santoso",
    "no_hp": "08123456789",
    "alamat": "Jl. Cendrawasih No. 1, Timika",
    "saldo": "0.00",
    "poin": 0,
    "is_active": true
  },
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc140"
  }
}
```

Validation errors `400`:
```json
{
  "success": false,
  "status_code": 400,
  "message": "Satu atau lebih field tidak valid.",
  "code": "VALIDATION_ERROR",
  "data": null,
  "errors": {
    "username": ["Username sudah digunakan."],
    "password": ["Password minimal 6 karakter."],
    "setuju_kebijakan_data": ["Anda harus menyetujui kebijakan data pribadi."]
  },
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc141"
  }
}
```

---

### 6.3 Kategori Sampah

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| `GET` | `/api/waste-categories/` | Public | Semua |
| `GET` | `/api/waste-categories/{id}/` | Public | Semua |
| `POST` | `/api/waste-categories/` | JWT | Admin, Koordinator |
| `PATCH` | `/api/waste-categories/{id}/` | JWT | Admin, Koordinator |
| `DELETE` | `/api/waste-categories/{id}/` | JWT | Admin |

**GET /api/waste-categories/ — Response `200 OK`:**
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "nama": "Plastik PET",
      "harga_beli_per_kg": "3000.00",
      "stok_terkini_kg": "150.50"
    },
    {
      "id": 2,
      "nama": "Gelas Plastik",
      "harga_beli_per_kg": "4000.00",
      "stok_terkini_kg": "75.00"
    }
  ]
}
```

**POST /api/waste-categories/ — Request:**
```json
{
  "nama": "Plastik PET",
  "harga_beli_per_kg": "3000.00"
}
```

---

### 6.4 Transaksi Setoran

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| `GET` | `/api/deposits/` | JWT | Owner, Petugas, Admin, Koordinator |
| `GET` | `/api/deposits/{id}/` | JWT | Owner, Petugas, Admin, Koordinator |
| `POST` | `/api/deposits/` | JWT | Petugas, Admin |

**POST /api/deposits/ — Input Setoran**

Request:
```json
{
  "nasabah": 5,
  "details": [
    {
      "kategori": 1,
      "berat_kg": "5.00"
    },
    {
      "kategori": 3,
      "berat_kg": "3.50"
    }
  ]
}
```

> **Catatan:** `harga_saat_itu` dan `subtotal` dihitung server-side. `petugas` diisi otomatis dari user login.

Response `201 Created`:
```json
{
  "id": 42,
  "nasabah": 5,
  "petugas": 2,
  "tanggal": "2026-07-07T10:30:00+09:00",
  "total_nilai": "20250.00",
  "status": "selesai",
  "details": [
    {
      "id": 80,
      "kategori": 1,
      "kategori_nama": "Plastik PET",
      "berat_kg": "5.00",
      "harga_saat_itu": "3000.00",
      "subtotal": "15000.00"
    },
    {
      "id": 81,
      "kategori": 3,
      "kategori_nama": "Kardus",
      "berat_kg": "3.50",
      "harga_saat_itu": "1500.00",
      "subtotal": "5250.00"
    }
  ],
  "poin_didapat": 20,
  "saldo_nasabah_baru": "145250.00"
}
```

Business error `422`:
```json
{
  "success": false,
  "status_code": 422,
  "message": "Berat setoran per jenis minimal 1 kg.",
  "code": "MIN_WEIGHT_NOT_MET",
  "data": null,
  "errors": {
    "details": [
      {
        "kategori": 1,
        "berat_kg": ["Minimal 1 kg per jenis sampah."]
      }
    ]
  },
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc150"
  }
}
```

**Side effects (atomik):**
- `nasabah.saldo` += `total_nilai`
- `nasabah.poin` += `floor(total_nilai / 1000)`
- `kategori.stok_terkini_kg` += `berat_kg` per detail

---

### 6.5 Penjemputan

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| `POST` | `/api/pickups/` | JWT | Nasabah |
| `GET` | `/api/pickups/` | JWT | Owner, Petugas, Admin |
| `GET` | `/api/pickups/{id}/` | JWT | Owner, Petugas, Admin |
| `PATCH` | `/api/pickups/{id}/` | JWT | Admin, Petugas (assigned) |
| `POST` | `/api/pickups/{id}/approve/` | JWT | Admin |
| `POST` | `/api/pickups/{id}/reject/` | JWT | Admin |
| `POST` | `/api/pickups/{id}/assign/` | JWT | Admin |
| `POST` | `/api/pickups/{id}/update-status/` | JWT | Petugas (assigned), Admin |

**POST /api/pickups/ — Ajukan Penjemputan**

Request:
```json
{
  "estimasi_berat": "8.00",
  "alamat_jemput": "Jl. Cendrawasih Poros SP.II, Timika",
  "jadwal": "2026-07-08T09:00:00+09:00",
  "catatan": "Sampah sudah dipilah di depan rumah"
}
```

Response `201 Created`:
```json
{
  "id": 10,
  "nasabah": 5,
  "nasabah_nama": "Budi Santoso",
  "petugas": null,
  "estimasi_berat": "8.00",
  "alamat_jemput": "Jl. Cendrawasih Poros SP.II, Timika",
  "jadwal": "2026-07-08T09:00:00+09:00",
  "status": "menunggu",
  "catatan": "Sampah sudah dipilah di depan rumah",
  "tanggal_pengajuan": "2026-07-07T10:00:00+09:00"
}
```

**POST /api/pickups/{id}/assign/ — Tugaskan Petugas**

Request:
```json
{
  "petugas_id": 3,
  "jadwal": "2026-07-08T09:00:00+09:00"
}
```

Response `200 OK`:
```json
{
  "id": 10,
  "status": "dijadwalkan",
  "petugas": 3,
  "petugas_nama": "Petugas A",
  "message": "Petugas berhasil ditugaskan."
}
```

**Status flow:**
```
menunggu → disetujui → dijadwalkan → dalam_perjalanan → dijemput → selesai
menunggu → ditolak
```

Invalid transition `409`:
```json
{
  "success": false,
  "status_code": 409,
  "message": "Tidak dapat mengubah status dari 'menunggu' ke 'selesai'.",
  "code": "INVALID_STATUS_TRANSITION",
  "data": null,
  "errors": null,
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc160"
  }
}
```

---

### 6.6 Penarikan Saldo

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| `POST` | `/api/withdrawals/` | JWT | Nasabah |
| `GET` | `/api/withdrawals/` | JWT | Owner, Admin, Koordinator |
| `GET` | `/api/withdrawals/{id}/` | JWT | Owner, Admin, Koordinator |
| `POST` | `/api/withdrawals/{id}/approve/` | JWT | Admin, Koordinator |
| `POST` | `/api/withdrawals/{id}/reject/` | JWT | Admin, Koordinator |

**POST /api/withdrawals/ — Ajukan Penarikan**

Request:
```json
{
  "nominal": "100000.00",
  "metode": "tunai"
}
```

Response `201 Created`:
```json
{
  "id": 7,
  "nasabah": 5,
  "nominal": "100000.00",
  "metode": "tunai",
  "status": "menunggu",
  "tanggal": "2026-07-07T11:00:00+09:00"
}
```

**POST /api/withdrawals/{id}/approve/ — Setujui (admin bayar manual, lalu approve)**

Response `200 OK`:
```json
{
  "id": 7,
  "status": "selesai",
  "nominal": "100000.00",
  "saldo_nasabah_baru": "45250.00",
  "message": "Penarikan saldo berhasil disetujui."
}
```

---

### 6.7 Reward & Penukaran Poin

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| `GET` | `/api/rewards/` | Public | Semua |
| `POST` | `/api/rewards/` | JWT | Admin |
| `PATCH` | `/api/rewards/{id}/` | JWT | Admin |
| `DELETE` | `/api/rewards/{id}/` | JWT | Admin |
| `POST` | `/api/reward-redemptions/` | JWT | Nasabah |
| `GET` | `/api/reward-redemptions/` | JWT | Owner, Admin |
| `POST` | `/api/reward-redemptions/{id}/approve/` | JWT | Admin |

**GET /api/rewards/ — Response `200 OK`:**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "nama": "Pulsa Rp10.000",
      "poin_dibutuhkan": 100,
      "stok": 50
    },
    {
      "id": 2,
      "nama": "Bibit Tanaman",
      "poin_dibutuhkan": 50,
      "stok": 30
    }
  ]
}
```

**POST /api/reward-redemptions/ — Request:**
```json
{
  "reward": 1
}
```

Response `201 Created`:
```json
{
  "id": 3,
  "nasabah": 5,
  "reward": 1,
  "reward_nama": "Pulsa Rp10.000",
  "poin_dibutuhkan": 100,
  "status": "menunggu",
  "tanggal": "2026-07-07T12:00:00+09:00"
}
```

---

### 6.8 Mitra Pengepul & Penjualan

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| `GET` | `/api/partners/` | JWT | Admin, Koordinator |
| `POST` | `/api/partners/` | JWT | Admin |
| `PATCH` | `/api/partners/{id}/` | JWT | Admin |
| `GET` | `/api/partner-sales/` | JWT | Admin, Koordinator |
| `POST` | `/api/partner-sales/` | JWT | Admin |
| `GET` | `/api/inventory/` | JWT | Admin, Koordinator, Pemerintah |

**POST /api/partner-sales/ — Catat Penjualan ke Mitra**

Request:
```json
{
  "mitra": 1,
  "kategori": 1,
  "berat_jual_kg": "100.00",
  "harga_jual_per_kg": "2500.00"
}
```

Response `201 Created`:
```json
{
  "id": 5,
  "mitra": 1,
  "mitra_nama": "PT Pengepul Timika",
  "kategori": 1,
  "kategori_nama": "Plastik PET",
  "berat_jual_kg": "100.00",
  "harga_jual_per_kg": "2500.00",
  "total_penjualan": "250000.00",
  "stok_kategori_baru": "50.50",
  "tanggal": "2026-07-07T14:00:00+09:00"
}
```

---

### 6.9 Pengaduan

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| `POST` | `/api/complaints/` | JWT | Nasabah |
| `GET` | `/api/complaints/` | JWT | Owner, Admin |
| `GET` | `/api/complaints/{id}/` | JWT | Owner, Admin |
| `PATCH` | `/api/complaints/{id}/` | JWT | Admin |

**POST /api/complaints/ — Request:**
```json
{
  "jenis_pengaduan": "saldo_belum_masuk",
  "keluhan": "Setoran kemarin belum masuk ke saldo saya."
}
```

**Jenis pengaduan (enum):**
`saldo_belum_masuk`, `penjemputan_terlambat`, `berat_tidak_sesuai`, `harga_tidak_sesuai`, `petugas_tidak_datang`, `kesalahan_data`, `bukti_tidak_muncul`

Response `201 Created`:
```json
{
  "id": 12,
  "nasabah": 5,
  "jenis_pengaduan": "saldo_belum_masuk",
  "keluhan": "Setoran kemarin belum masuk ke saldo saya.",
  "status": "terbuka",
  "tindak_lanjut": "",
  "tanggal": "2026-07-07T13:00:00+09:00"
}
```

**PATCH /api/complaints/{id}/ — Admin tindak lanjut**

Request:
```json
{
  "tindak_lanjut": "Saldo sudah diperbaiki dan dikonfirmasi ke nasabah via WA.",
  "status": "ditutup"
}
```

---

### 6.10 Riwayat Transaksi Gabungan

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| `GET` | `/api/activity/` | JWT | Nasabah (milik sendiri), Admin |

```
GET /api/activity/?jenis=setoran&page=1&ordering=-tanggal
```

Response `200 OK`:
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/activity/?page=2",
  "previous": null,
  "results": [
    {
      "id": 42,
      "type": "setoran",
      "tanggal": "2026-07-07T10:30:00+09:00",
      "nominal": "20250.00",
      "status": "selesai",
      "keterangan": "Setoran 2 jenis sampah"
    },
    {
      "id": 7,
      "type": "penarikan",
      "tanggal": "2026-07-06T15:00:00+09:00",
      "nominal": "100000.00",
      "status": "selesai",
      "keterangan": "Penarikan tunai"
    },
    {
      "id": 3,
      "type": "penukaran_poin",
      "tanggal": "2026-07-05T11:00:00+09:00",
      "nominal": null,
      "poin": 100,
      "status": "selesai",
      "keterangan": "Pulsa Rp10.000"
    }
  ]
}
```

---

### 6.11 Dashboard

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| `GET` | `/api/dashboard/overview/` | JWT | Admin, Koordinator, Pemerintah |
| `GET` | `/api/dashboard/deposit-chart/` | JWT | Admin, Koordinator, Pemerintah |
| `GET` | `/api/dashboard/recent-activity/` | JWT | Admin, Koordinator, Pemerintah |

**GET /api/dashboard/overview/ — Response `200 OK`:**
```json
{
  "total_nasabah": 250,
  "nasabah_aktif_30_hari": 85,
  "total_sampah_kg": "1250.50",
  "total_nilai_setoran": "15750000.00",
  "total_penarikan": "8500000.00",
  "total_penukaran_poin": 45,
  "penjemputan_menunggu": 3,
  "pengaduan_terbuka": 2,
  "stok_per_kategori": [
    {
      "kategori_id": 1,
      "nama": "Plastik PET",
      "stok_kg": "150.50"
    }
  ],
  "periode": {
    "start": "2026-07-01T00:00:00+09:00",
    "end": "2026-07-07T23:59:59+09:00"
  }
}
```

**GET /api/dashboard/deposit-chart/?bulan=7&tahun=2026:**
```json
{
  "labels": ["01", "02", "03", "04", "05", "06", "07"],
  "datasets": [
    {
      "label": "Tonase (kg)",
      "data": [45.5, 52.0, 38.5, 60.0, 55.5, 48.0, 62.5]
    },
    {
      "label": "Nilai (Rp juta)",
      "data": [0.5, 0.6, 0.4, 0.7, 0.6, 0.5, 0.7]
    }
  ]
}
```

---

### 6.12 Laporan

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| `GET` | `/api/reports/daily/` | JWT | Admin, Koordinator, Pemerintah |
| `GET` | `/api/reports/weekly/` | JWT | Admin, Koordinator, Pemerintah |
| `GET` | `/api/reports/monthly/` | JWT | Admin, Koordinator, Pemerintah |
| `GET` | `/api/reports/waste/` | JWT | Admin, Koordinator, Pemerintah |
| `GET` | `/api/reports/evaluation/` | JWT | Admin, Koordinator, Pemerintah |

**GET /api/reports/daily/?tanggal=2026-07-07 — Response `200 OK`:**
```json
{
  "tanggal": "2026-07-07",
  "jumlah_transaksi_setoran": 12,
  "total_setoran": "450000.00",
  "total_penarikan": "200000.00",
  "jumlah_penjemputan_selesai": 3,
  "jumlah_penukaran_poin": 2,
  "tonase_per_jenis": [
    {
      "kategori": "Plastik PET",
      "berat_kg": "35.50",
      "nilai": "106500.00"
    },
    {
      "kategori": "Kardus",
      "berat_kg": "28.00",
      "nilai": "42000.00"
    }
  ],
  "nasabah_baru": 2
}
```

**GET /api/reports/monthly/?bulan=7&tahun=2026 — Response `200 OK`:**
```json
{
  "bulan": 7,
  "tahun": 2026,
  "jumlah_nasabah_terdaftar": 250,
  "jumlah_nasabah_aktif": 85,
  "total_sampah_kg": "1250.50",
  "total_nilai_ekonomi": "15750000.00",
  "jumlah_penjemputan_selesai": 45,
  "total_saldo_nasabah": "3200000.00",
  "jumlah_reward_diberikan": 15,
  "tonase_per_jenis": [],
  "wilayah_teraktif": [],
  "kendala_lapangan": [],
  "rekomendasi": []
}
```

---

### 6.13 Pengaturan Institusi

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| `GET` | `/api/settings/` | Public | Semua |
| `PATCH` | `/api/settings/` | JWT | Admin |

**GET /api/settings/ — Response `200 OK`:**
```json
{
  "nama_institusi": "Bank Sampah MIRU - Distrik Mimika Baru",
  "alamat": "Jl. Cendrawasih Poros SP.II, Timika, Papua Tengah 99910",
  "kontak": "0821 977 3693",
  "email": "distrikmiru@mimikakab.go.id",
  "logo_url": null,
  "jam_operasional": "Senin–Sabtu, 08.00–17.00 WIT",
  "pengumuman": "Selamat datang di MIRU Bank Sampah!"
}
```

---

### 6.14 Audit Log

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| `GET` | `/api/audit-log/` | JWT | Admin |

```
GET /api/audit-log/?user=2&model=TransaksiSetoran&date_after=2026-07-01
```

Response `200 OK`:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 101,
      "user": 2,
      "user_nama": "Admin Harorld",
      "action": "update",
      "model_name": "TransaksiSetoran",
      "object_id": 42,
      "changes": {
        "total_nilai": { "old": "19000.00", "new": "19500.00" }
      },
      "timestamp": "2026-07-07T16:00:00+09:00",
      "ip_address": "192.168.1.10"
    }
  ]
}
```

---

## 7. OpenAPI / Swagger

| Resource | URL |
|----------|-----|
| Swagger UI | `GET /api/docs/` |
| OpenAPI Schema (JSON) | `GET /api/schema/` |
| ReDoc (opsional) | `GET /api/redoc/` |

Semua endpoint harus memiliki:
- Tag grouping per modul
- `help_text` pada setiap field serializer
- Contoh request/response di schema
- Dokumentasi error response

---

## 8. Rate Limiting (Target Fase 7)

| Endpoint | Limit |
|----------|-------|
| `POST /api/auth/login/` | 10 request / menit / IP |
| `POST /api/auth/refresh/` | 30 request / menit / user |
| Endpoint write (POST/PATCH) | 100 request / jam / user |
| Endpoint read (GET) | 1000 request / jam / user |

Response `429 Too Many Requests`:
```json
{
  "success": false,
  "status_code": 429,
  "message": "Terlalu banyak permintaan. Coba lagi dalam 60 detik.",
  "code": "RATE_LIMIT_EXCEEDED",
  "data": null,
  "errors": null,
  "meta": {
    "timestamp": "2026-07-07T14:30:00+09:00",
    "request_id": "req_abc170",
    "retry_after": 60
  }
}
```

---

## 9. Versioning

| Versi | Prefix | Status |
|-------|--------|--------|
| v1 (current) | `/api/` | Aktif |
| v2 (future) | `/api/v2/` | Jika ada breaking change |

Breaking change policy:
- Field baru: backward compatible (tidak perlu versi baru)
- Field dihapus / diubah tipe: butuh versi baru
- Deprecation notice: minimal 3 bulan sebelum sunset

---

## 10. Mapping Role → Endpoint Access

| Endpoint Group | Nasabah | Petugas | Admin | Koordinator | Pemerintah |
|----------------|---------|---------|-------|-------------|------------|
| Auth (login/register) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Kategori (read) | ✅ Public | ✅ | ✅ | ✅ | ✅ |
| Kategori (write) | ❌ | ❌ | ✅ | ✅ | ❌ |
| Transaksi setoran (create) | ❌ | ✅ | ✅ | ❌ | ❌ |
| Transaksi (read own) | ✅ | ✅ all | ✅ all | ✅ all | ❌ |
| Penjemputan (create) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Penjemputan (manage) | ❌ | ✅ assigned | ✅ | ❌ | ❌ |
| Penarikan (create) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Penarikan (approve) | ❌ | ❌ | ✅ | ✅ | ❌ |
| Reward (read) | ✅ Public | ✅ | ✅ | ✅ | ✅ |
| Penukaran (create) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Pengaduan (create) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Pengaduan (manage) | ❌ | ❌ | ✅ | ❌ | ❌ |
| Gudang/Mitra | ❌ | ❌ | ✅ | ✅ read | ❌ |
| Dashboard | ❌ | ❌ | ✅ | ✅ | ✅ read |
| Laporan | ❌ | ❌ | ✅ | ✅ | ✅ read |
| Audit Log | ❌ | ❌ | ✅ | ❌ | ❌ |
| Pengaturan (write) | ❌ | ❌ | ✅ | ❌ | ❌ |

---

## 11. Catatan Implementasi

### Status Saat Ini vs Target

| Aspek | Saat Ini | Target (Fase 1–6) |
|-------|----------|-------------------|
| Response format | DRF default (resource langsung) | JSON Envelope (`success`, `status_code`, `message`, `data`, `meta`) |
| Error format | DRF default | JSON Envelope error (`success: false`, `code`, `errors`) |
| Pagination | Belum dikonfigurasi | `meta.pagination` dalam envelope |
| `/api/auth/me/` | Belum ada | Fase 1 |
| Action endpoints (approve/reject) | Belum ada | Fase 3 |
| Dashboard & Laporan | Belum ada | Fase 4 |
| Audit log | Belum ada | Fase 5 |
| `harga_saat_itu` auto-calculate | Client-side | Server-side (Fase 2) |
| `details` di response GET transaksi | write_only | Nested read (Fase 2) |

### Konvensi Frontend

- **Selalu cek `success` boolean** sebelum memproses `data`
- **Tampilkan `message`** ke user (toast/alert) — sudah Bahasa Indonesia
- **Gunakan `errors` object** untuk highlight field form yang invalid
- **Jangan andalkan HTTP status saja** — parse `status_code` dari body sebagai fallback
- Simpan `access` token di memory / secure storage (mobile: `flutter_secure_storage`)
- Simpan `refresh` token di secure storage
- Refresh otomatis saat `success === false` && `code === "AUTHENTICATION_FAILED"`
- Pagination: baca dari `meta.pagination` (bukan `count`/`results` di root)
- Format tanggal tampilan: konversi ISO 8601 ke locale `id-ID` di frontend
- Format rupiah: `Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR' })`

**Contoh handler frontend:**
```typescript
async function apiCall<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  const json = await res.json();

  if (!json.success) {
    throw new ApiError(json.message, json.code, json.errors, json.status_code);
  }
  return json.data as T;
}
```
