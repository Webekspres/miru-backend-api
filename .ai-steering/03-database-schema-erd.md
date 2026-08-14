# 03 — Database Schema & ERD (Backend Django)

## Diagram Relasi Antar Tabel

```
┌──────────────────┐       ┌─────────────────────────┐
│      User        │       │   TransaksiSetoran       │
│──────────────────│       │─────────────────────────│
│ PK id            │◄──────│ FK nasabah              │
│ username (unique)│       │ FK petugas (nullable)   │
│ password         │       │ tanggal (auto_now_add)  │
│ role             │       │ total_nilai (Decimal)   │
│ nama_lengkap     │       │ status: selesai         │
│ no_hp            │       └───────────┬─────────────┘
│ alamat           │                   │ 1
│ saldo (Decimal)  │       ┌───────────┴─────────────┐
│ poin (Integer)   │       │   DetailSetoran          │
│ email            │       │─────────────────────────│
│ is_active        │       │ PK id                   │
└──────┬──────┬────┘       │ FK transaksi            │
       │      │            │ FK kategori             │
       │      │            │ berat_kg (Decimal)      │
       │      │            │ harga_saat_itu (Decimal)│
       │      │            │ subtotal (Decimal)      │
       │      │            └─────────────────────────┘
       │      │
       │      │    ┌──────────────────┐
       │      │    │ Penjemputan      │
       │      │    │──────────────────│
       │      └────│ FK nasabah       │
       │           │ FK petugas(null) │
       │           │ estimasi_berat   │
       │           │ alamat_jemput    │
       │           │ jadwal           │
       │           │ status (enum)    │
       │           └──────────────────┘
       │
       │    ┌──────────────────┐       ┌──────────────────┐
       │    │ PenarikanSaldo   │       │  Reward          │
       │    │──────────────────│       │──────────────────│
       └────│ FK nasabah       │       │ PK id            │
            │ nominal          │       │ nama             │
            │ metode           │       │ poin_dibutuhkan  │
            │ status           │       │ stok             │
            │ tanggal          │       └────────┬─────────┘
            └──────────────────┘                │
                                                 │
            ┌──────────────────┐       ┌────────┴─────────┐
            │ PenukaranPoin    │       │  KategoriSampah   │
            │──────────────────│       │──────────────────│
            │ FK nasabah       │       │ PK id            │
            │ FK reward        │       │ nama             │
            │ status           │◄──────│ harga_beli_per_kg│
            │ tanggal          │       │ stok_terkini_kg  │
            └──────────────────┘       └────────┬─────────┘
                                                 │
            ┌──────────────────┐       ┌────────┴─────────┐
            │ PenjualanMitra   │       │ MitraPengepul     │
            │──────────────────│       │──────────────────│
            │ FK mitra         │◄──────│ PK id            │
            │ FK kategori      │       │ nama             │
            │ berat_jual_kg    │       │ kontak           │
            │ harga_jual_per_kg│       └──────────────────┘
            │ total_penjualan  │
            │ tanggal          │
            └──────────────────┘

┌──────────────────┐
│   Pengaduan      │
│──────────────────│
│ PK id            │
│ FK nasabah       │
│ keluhan (Text)   │
│ status           │
│ tanggal          │
│ tindak_lanjut(T) │
└──────────────────┘
```

## Detail Setiap Tabel

### 1. User (extends AbstractUser)
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField (PK) | Primary Key |
| username | CharField(150) | unique, required |
| password | CharField(128) | write-only |
| role | CharField(20) | choices: nasabah, petugas, admin, koordinator |
| nama_lengkap | CharField(255) | required |
| no_hp | CharField(15) | blank=True |
| alamat | TextField | blank=True |
| saldo | DecimalField(12,2) | default=0 |
| poin | IntegerField | default=0 |
| email | EmailField | inherited from AbstractUser |
| is_active | BooleanField | inherited, default=True |

**Indexes**: username (unique), role, no_hp

### 2. KategoriSampah
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField (PK) | Primary Key |
| nama | CharField(100) | required |
| harga_beli_per_kg | DecimalField(10,2) | required |
| stok_terkini_kg | DecimalField(10,2) | default=0 |

**Seed Data**: Plastik, Kertas, Kardus, Logam, Aluminium, Kaca, Minyak Jelantah, Organik, Elektronik

### 3. TransaksiSetoran
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField (PK) | Primary Key |
| nasabah | FK(User) | CASCADE, related: setoran_nasabah |
| petugas | FK(User) | SET_NULL, nullable, related: setoran_petugas |
| tanggal | DateTimeField | auto_now_add |
| total_nilai | DecimalField(12,2) | default=0 |
| status | CharField(20) | default='selesai' |

**Logic**: Status langsung 'selesai' untuk setoran langsung (sesuai SOP)

### 4. DetailSetoran
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField (PK) | Primary Key |
| transaksi | FK(TransaksiSetoran) | CASCADE, related: details |
| kategori | FK(KategoriSampah) | RESTRICT |
| berat_kg | DecimalField(8,2) | required |
| harga_saat_itu | DecimalField(10,2) | harga dari kategori saat transaksi |
| subtotal | DecimalField(12,2) | berat_kg × harga_saat_itu |

### 5. Penjemputan
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField (PK) | Primary Key |
| nasabah | FK(User) | CASCADE, related: penjemputan_nasabah |
| petugas | FK(User) | SET_NULL, nullable, related: penjemputan_petugas |
| estimasi_berat | DecimalField(8,2) | required, >= 5 kg |
| alamat_jemput | TextField | required |
| jadwal | DateTimeField | required |
| status | CharField(20) | choices: menunggu, disetujui, dijadwalkan, dalam_perjalanan, dijemput, selesai, ditolak |

**Status Flow**: menunggu → disetujui → dijadwalkan → dalam_perjalanan → dijemput → selesai
**Rejection**: menunggu → ditolak

### 6. PenarikanSaldo
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField (PK) | Primary Key |
| nasabah | FK(User) | CASCADE |
| nominal | DecimalField(12,2) | required, >= 50000 |
| metode | CharField(50) | 'tunai' (default), 'transfer' |
| lampiran_ktp | FileField | nullable; wajib jika nominal ≥ 1.000.000; **dihapus** setelah proses |
| ktp_diverifikasi | Boolean | True setelah lampiran diproses & file dihapus |
| status | CharField(20) | choices: menunggu, selesai, ditolak |
| tanggal | DateTimeField | auto_now_add |

**Logic**: Saat status diubah ke 'selesai', kurangi saldo nasabah (manual payment oleh admin)
**Constraint**: nominal >= 50000 (sesuai SOP)

### 7. Reward
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField (PK) | Primary Key |
| nama | CharField(100) | required |
| poin_dibutuhkan | IntegerField | required |
| stok | IntegerField | default=0 |

### 8. PenukaranPoin
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField (PK) | Primary Key |
| nasabah | FK(User) | CASCADE |
| reward | FK(Reward) | RESTRICT |
| status | CharField(20) | choices: menunggu, selesai |
| tanggal | DateTimeField | auto_now_add |

**Logic**: Saat status 'selesai', kurangi poin nasabah, kurangi stok reward

### 9. MitraPengepul
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField (PK) | Primary Key |
| nama | CharField(100) | required |
| kontak | CharField(50) | bisa nomor HP, email, dll |

### 10. PenjualanMitra
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField (PK) | Primary Key |
| mitra | FK(MitraPengepul) | CASCADE |
| kategori | FK(KategoriSampah) | RESTRICT |
| berat_jual_kg | DecimalField(8,2) | required |
| harga_jual_per_kg | DecimalField(10,2) | required |
| total_penjualan | DecimalField(12,2) | computed: berat × harga |
| tanggal | DateTimeField | auto_now_add |

**Logic**: Saat penjualan dibuat, kurangi stok_terkini_kg dari kategori sampah

### 11. Pengaduan
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField (PK) | Primary Key |
| nasabah | FK(User) | CASCADE |
| keluhan | TextField | required |
| status | CharField(20) | choices: terbuka, ditutup |
| tanggal | DateTimeField | auto_now_add |
| tindak_lanjut | TextField | blank=True, diisi admin |

## Ringkasan Aturan Constraints

| Aturan | Nilai | Berlaku di |
|--------|-------|------------|
| Minimal setoran | >= 1 kg per jenis | Validasi serializer DetailSetoran |
| Minimal penjemputan | >= 5 kg estimasi | Validasi serializer Penjemputan |
| Konversi poin | 1 poin = Rp1.000 setoran | Logika di TransaksiSetoranSerializer.create() |
| Minimal tarik saldo | >= Rp50.000 | Validasi serializer PenarikanSaldo |
| Pencairan saldo | MANUAL (tunai/transfer) | Tidak ada integrasi payment gateway |
| Stok sampah | Update otomatis saat setor/jual | Via perform_create / serializer |
