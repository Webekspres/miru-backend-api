# 11 — Security & Privacy (Backend — Sumber Kanonik)

> **Dokumen ini** adalah pedoman keamanan & privasi sistem MIRU Bank Sampah.
> Versi backend ini bersifat **sumber kanonik**; web-admin dan mobile **wajib selaras**
> dan punya penjabaran platform di `.ai-steering/11-security-and-privacy.md` masing-masing.
>
> **Referensi persyaratan:**
> - UU No. 27/2022 tentang Pelindungan Data Pribadi (PDP)
> - `Jawaban_Persyaratan_MIRU_Bank_Sampah.md` §6.3, §6.5–6.6
> - `06-system-constraints.md`
> - `04-api-contracts-and-standards.md` (JWT, envelope)
> - Proposal §5 batasan pengembangan
>
> **Implementasi dijadwalkan di:** `08-task-list.md` (Fase 7 + checklist keamanan)

---

## 1. Prinsip Keamanan Ekosistem

| # | Prinsip | Arti praktis |
|---|---------|--------------|
| 1 | **Defense in depth** | Validasi di serializer + permission + DB constraint; jangan andalkan satu lapis |
| 2 | **Least privilege** | Setiap role hanya data & aksi yang diizinkan (`permissions.py` + queryset filter) |
| 3 | **Zero trust input** | Semua input dari client dianggap berbahaya — validasi DRF |
| 4 | **Secrets out of code** | `SECRET_KEY`, DB, API key hanya di environment / secret store |
| 5 | **Encrypt in transit** | HTTPS wajib di production (Jawaban §6.5.4) |
| 6 | **Minimize PII** | NIK/foto KTP hanya bila perlu (penarikan besar); jangan log PII |
| 7 | **Auditability** | Perubahan kritis tercatat di `AuditLog` |
| 8 | **Fail closed** | Default deny pada permission; error bisnis tidak bocorkan detail internal |

### Batas yang TIDAK boleh dilanggar (security-related)

- ❌ Payment gateway otomatis
- ❌ Expose password / refresh token di response body selain login yang disepakati
- ❌ Integrasi Dukcapil tanpa addendum legal
- ❌ Multi-tenant data leakage antar organisasi (sistem single-tenant)
- ❌ Mitra/pengepul punya akun login

---

## 2. Klasifikasi Data

| Kelas | Contoh | Perlakuan |
|-------|--------|-----------|
| **Rahasia sistem** | `SECRET_KEY`, JWT signing, DB password, Maps/FCM/WA API key | Env only; rotasi; tidak di log/repo |
| **PII sensitif** | NIK, foto KTP | Enkripsi at-rest (Fase 8); akses admin terbatas; mask di UI |
| **PII operasional** | Nama, no HP, alamat, kelurahan | Hanya untuk operasional bank sampah; retensi sesuai kebijakan (arsip 5 thn transaksi) |
| **Keuangan** | Saldo, poin, transaksi, penarikan | Atomic ledger; audit; anti double-processing |
| **Publik** | Kategori sampah, harga aktif, pengumuman aktif, settings institusi (sebagian) | Boleh tanpa auth bila sudah ditandai Public di kontrak API |
| **Internal ops** | Audit log, laporan, stok, penjualan mitra | Staff/role-gated |

### Consent & PDP

- Registrasi nasabah: `setuju_kebijakan_data = true` **wajib**
- Endpoint / halaman kebijakan privasi harus tersedia untuk Play Store & publikasi
- Data tidak dibagikan ke pihak ketiga di luar operasional program
- Koreksi data transaksi: admin only + audit log

---

## 3. Autentikasi & Sesi (JWT)

| Aturan | Nilai / perilaku |
|--------|------------------|
| Access token | JWT, expiry **24 jam** (constraint proyek) |
| Refresh token | Wajib untuk perpanjang sesi; jangan “infinite refresh” tanpa expiry |
| Transport | Hanya lewat `Authorization: Bearer …` |
| Password | Hash Django; min 6 karakter (aturan bisnis registrasi); **write_only** di serializer |
| Login endpoints | Rate limit ketat (lihat §5) |
| Role di claim/response | Digunakan client untuk redirect — **bukan** satu-satunya otorisasi (server wajib re-check) |

### Endpoint auth (kontrak)

- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET|PATCH /api/auth/me/`
- Registrasi nasabah: `POST /api/users/` (role default `nasabah`)

### Aturan anti-abuse auth

- Jangan kembalikan apakah username sudah ada dengan pesan yang membedakan secara kasar (hindari user enumeration berlebihan)
- Blokir login gagal beruntun via rate limit
- Jangan log password atau token mentah

---

## 4. Otorisasi (RBAC)

Otorisasi **selalu di server**. Matriks ringkas:

| Role | Prinsip |
|------|---------|
| `nasabah` | Hanya data milik sendiri; tidak create setoran |
| `petugas` | Setoran + update penjemputan assigned |
| `admin` | Full operasional |
| `koordinator` | Read-heavy + approve tertentu sesuai permission |
| `pemerintah` | **Read-only** dashboard & laporan |
| Mitra | **Tidak ada akun** |

Wajib:

- `permission_classes` pada setiap view
- `get_queryset()` filter per role (object-level)
- Tolak elevasi role / ubah `saldo` / `poin` dari PATCH nasabah

Detail modul: `07-modules-and-features.md`, `10`-equivalents di frontend.

---

## 5. Proteksi API & Konfigurasi Production

### 5.1 Rate limiting (wajib sebelum go-live)

| Target | Batas |
|--------|-------|
| `/api/auth/login/` | **10 / menit** per IP (atau setara DRF throttle) |
| Endpoint write (POST/PATCH/DELETE) | **100 / jam** per user terautentikasi |
| Public read (kategori, dll.) | Throttle longgar wajar anti-scrape |

### 5.2 HTTPS & header Django production

- SSL termination di Nginx (Jawaban §6.5.4)
- `DEBUG=False`
- `SECURE_SSL_REDIRECT=True`
- `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`
- `SECURE_HSTS_SECONDS` (nilai wajar setelah HTTPS stabil)
- `ALLOWED_HOSTS` ketat dari env
- CORS **whitelist** origin production (web-admin + domain resmi) — **bukan** `*`

### 5.3 CORS

| Environment | Kebijakan |
|-------------|-----------|
| Development | Localhost / LAN IP terbatas |
| Production | Hanya origin web-admin & domain resmi klien |

Mobile native tidak memakai CORS browser, tetapi tetap butuh HTTPS + JWT valid.

### 5.4 Header & response hygiene

- Jangan expose stack trace ke client (`DEBUG=False`)
- Envelope error standar — pesan ramah; detail teknis hanya di log server
- Tidak mengembalikan field `password`, secret, atau path filesystem

---

## 6. Integritas Transaksional (Keamanan Keuangan)

| Kontrol | Implementasi |
|---------|--------------|
| Atomic write | `transaction.atomic()` |
| Race condition saldo | `select_for_update()` |
| Saldo/stok/poin ≥ 0 | Validasi ledger |
| Double approve | Tolak jika status sudah final (`AlreadyProcessedError` / 409) |
| Harga dari server | `harga_saat_itu` dari DB, bukan percaya client |
| Audit koreksi | Admin only + `AuditLog` |

Ini adalah kontrol **keamanan finansial**, setara pentingnya dengan auth.

---

## 7. Upload, Media, & Data Sensitif

| Item | Aturan |
|------|--------|
| Foto KTP | Hanya untuk penarikan besar (persyaratan); simpan di media privat; akses role-gated |
| NIK | Field-level encryption (Fase 8); jangan log |
| Validasi file | Tipe MIME/ukuran max; larang executable |
| Media URL | Jangan buat bucket/public list semua KTP |
| PDF bukti | Generate server-side; auth wajib untuk unduh milik orang lain |

---

## 8. Logging, Monitoring, Incident

| Lapisan | Aturan |
|---------|--------|
| App log | Structured JSON di production; **redact** token, password, NIK |
| Error tracking | Sentry (atau setara) — scrub PII di before_send |
| Health | `GET /health/` — status + DB; **jangan** bocorkan versi sensitif berlebih |
| Audit | `AuditLog` untuk User, setoran, penarikan, kategori, pengaduan, dll. |
| Alert | Pantau spike 401/429 dan error 5xx |

### Respons insiden (ringkas)

1. Cabut/rotate `SECRET_KEY` / credential yang bocor  
2. Invalidate refresh token bila memungkinkan  
3. Catat di audit / laporan pengelola  
4. Patch + postmortem singkat  

---

## 9. Backup & Retensi (Keamanan Ketersediaan)

> Jawaban §6.5.6; Constraints §7–8.

- Backup **harian** DB terenkripsi
- Backup **mingguan** full; retensi ≥ **30 hari**; storage terpisah
- Test restore minimal 1× sebelum go-live
- Arsip transaksi digital minimal **5 tahun**
- Prosedur restore terdokumentasi (siapa yang boleh restore)

---

## 10. Secrets & Supply Chain

- `.env*` di `.gitignore`; sediakan `.env.example` tanpa nilai rahasia
- Dependensi: pin versi wajar; audit CVE rutin sebelum release
- Image Docker production: non-root jika memungkinkan; no `runserver`
- CI: jangan print secret; gunakan GitHub Secrets / setara

---

## 11. Integrasi Pihak Ketiga (Keamanan)

| Integrasi | Status | Catatan keamanan |
|-----------|--------|------------------|
| Google Maps (sederhana) | Fase 8 (Modul 7) | API key restrict by IP/bundle; kuota klien |
| FCM | Fase 8 (Modul 9) — backend ✅; client Flutter 🔲 | Server key / SA hanya di backend; validasi device token milik user |
| WhatsApp Business | Fase 8 (Modul 9) | Jangan kirim NIK/KTP; template message terbatas |
| Email transactional | Fase 8 (Modul 9) — ✅ sebagian | Kredensial SMTP di env; jangan CC data sensitif massal |
| Payment gateway | **Out of scope** | Dilarang Constraints/Proposal |

---

## 12. Checklist Go-Live Keamanan (Backend)

### Wajib (Fase 7)

- [ ] `DEBUG=False`, secrets dari env
- [ ] HTTPS + secure cookies / SSL redirect
- [ ] CORS whitelist production
- [ ] Rate limit login + write
- [ ] Gunicorn (bukan runserver) + Nginx
- [ ] Backup harian/mingguan + uji restore
- [ ] Logging terstruktur + Sentry (scrub PII)
- [ ] `/health/` aktif & dipantau
- [ ] Permission test lolos (nasabah tidak akses data orang lain)

### Fase 8 — Keamanan data (Pengembangan Lanjutan)

- [ ] Enkripsi NIK / KTP at-rest
- [ ] Upload KTP tersimpan aman + akses terbatas
- [ ] Lupa password dengan token berumur pendek
- [ ] Retensi/arsip 5 tahun terdefinisi operasional

---

## 13. Mapping ke Dokumen Lain

| Topik | Dokumen |
|-------|---------|
| Kontrak JWT & endpoint | `04-api-contracts-and-standards.md` |
| Larangan fitur | `06-system-constraints.md` |
| Role & modul | `07-modules-and-features.md` |
| Task implementasi | `08-task-list.md` §Fase 7 & 8.4 |
| PDP & consent | Jawaban §6.3; Modul registrasi |
| Web Admin controls | `web-admin/.ai-steering/11-security-and-privacy.md` |
| Mobile controls | `mirumobileapp/.ai-steering/11-security-and-privacy.md` |

---

## 14. Aturan untuk AI / Engineer

1. Setiap endpoint baru: tentukan auth + permission + queryset scope **sebelum** merge.  
2. Jangan hardcode secret atau matikan permission “sementara” di branch yang di-merge.  
3. Jangan log PII.  
4. Perubahan saldo/poin/stok harus lewat service ledger ber-`atomic`.  
5. Sebelum menandai “production ready”, lengkapi checklist §12.
