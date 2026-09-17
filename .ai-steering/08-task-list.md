# 08 — Task List: Backend

Belum selesai di atas; selesai di bawah.
Hanya task dalam 17 modul. Jangan tambah fitur tanpa addendum.

---

## Fase 7 — Production ready

### Bisa langsung

- [x] Test restore 1× sebelum go-live (`BACKUP.md` §7 + `scripts/restore.sh`)
  - DB restore → `/health/` OK → login admin + 1 transaksi baca
  - 2026-09-02 · habibiahmada · **lolos** · isolasi `miru_restore_test` (live `miru` tidak di-drop)

### Perlu integrasi

- [ ] Sentry + scrub PII di `before_send` — **ditunda**; butuh DSN; jangan kirim token/password/KTP

---

## Fase 8 — Pengembangan lanjutan

### Bisa langsung

- [ ] Bulk import nasabah CSV/Excel (admin/koordinator)
  - Validasi baris: username unik, password policy, role = nasabah
  - Consent `setuju_kebijakan_data` wajib; batasi ukuran file
  - Envelope: sukses N / gagal M + error per baris; audit log
  - Jangan import staff lewat endpoint yang sama
- [ ] Dokumentasi batasan Maps di kontrak API (bukan distance matrix / live tracking)
- [ ] Celery + Redis: email, FCM batch, export, backup trigger; retry + DLQ
- [ ] Redis cache `/api/dashboard/overview/` (TTL pendek)

### Perlu integrasi (kredensial, domain, traffic)

- [ ] WhatsApp Business API: setoran berhasil; penarikan disetujui/ditolak — **`WA_*`**
  - Payload tanpa KTP, saldo penuh, JWT; fallback in-app/FCM
- [ ] Maps API key di env, restrict IP/referrer/bundle — **key dari ops/klien**
- [ ] CORS + HTTPS production (`ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`) — **domain final**
- [ ] URL publik privacy policy untuk Play Store — **domain HTTPS final**
- [ ] API versioning `/api/v1/` — **hanya saat breaking change**
- [ ] CDN media — **hanya jika traffic media nyata** (bukan lampiran KTP)
- [ ] Read replica PostgreSQL — **hanya jika traffic baca nyata**

---

## Out of scope

- ❌ Payment gateway otomatis
- ❌ GPS live tracking
- ❌ Timbangan / barcode / printer auto
- ❌ API Dukcapil
- ❌ Multi-tenant
- ❌ Login mitra/pengepul

---

## Selesai

### Fase 0 — Foundation

- [x] Django `core/` + app `api`; Dockerfile; `.env.example`
- [x] DRF, simplejwt, django-filter, cors-headers, drf-spectacular, psycopg2
- [x] Model: User, KategoriSampah, TransaksiSetoran, Penjemputan, PenarikanSaldo, Reward, Mitra, Pengaduan
- [x] Router, permission role, JWT, `/health/`

### Fase 1 — Auth & envelope

- [x] Env secrets; WIT
- [x] Envelope `success` / `status_code` / `message` / `data` / `meta`
- [x] Pagination, filters, exception handler
- [x] Login, refresh, me, registrasi nasabah
- [x] `seed_data`; CRUD kategori

### Fase 2 — Bisnis inti

- [x] Ledger atomic + `select_for_update`
- [x] Setoran, penjemputan, penarikan, tukar poin, penjualan mitra, pengaduan
- [x] Queryset per role termasuk `pemerintah` read-only

### Fase 3 — Operasional

- [x] Approve/reject/assign setoran–jemput–tarik–tukar
- [x] `GET /api/activity/`; profil/QR; katalog reward

### Fase 4 — Monitoring & laporan

- [x] Dashboard overview / chart / recent activity
- [x] Laporan daily / weekly / monthly / waste / evaluation
- [x] Inventory + history

### Fase 5 — Governance

- [x] Audit log; pengaturan institusi; pengumuman
- [x] Riwayat harga; role pemerintah; consent UU PDP
- [x] NIK tidak disimpan; lampiran KTP penarikan besar dihapus setelah proses

### Fase 6 — Kualitas

- [x] Suite test (auth, deposits, pickups, withdrawals, permissions)
- [x] OpenAPI `/api/docs/`
- [x] Envelope error BI field-level; throttle login BI
- [x] Test isolasi permission nasabah

### Fase 7 (sebagian)

- [x] `DEBUG=False`; `SECRET_KEY` dari env; HTTPS/HSTS/cookie secure
- [x] Rate limit login + write; CORS whitelist di production
- [x] Gunicorn + Nginx; CI; backup `pg_dump` GPG; `restore.sh`
- [x] `/health/`; JSON logging; PII redact; indexes; Locust

### Fase 8 (sebagian)

- [x] CRUD edukasi; harga H-3 + pengumuman
- [x] Wilayah layanan + kuota 2×/minggu; kelurahan/RT-RW; `wilayah_teraktif`
- [x] Approve+assign jemput atomik; filter petugas; lat/lng opsional; validasi jadwal
- [x] Lupa password + OTP WA (kontrak); gate alamat; `phone_verified`
- [x] PDF bukti; lampiran KTP ≥1jt role-gated lalu hapus; metode transfer metadata
- [x] `expire_poin` 1 tahun; `PoinInfoView`
- [x] Notifikasi in-app + FCM (tanpa NIK/KTP/token); email admin
- [x] Export Excel; evaluasi kendala + rekomendasi; retensi 5 tahun
- [x] `GET /api/privacy-policy/`
- [x] Lookup nasabah setoran; notif setoran nilai benar
- [x] Snapshot poin pengajuan; status ditolak penukaran
- [x] Pengaduan `lainnya`; tutup wajib `tindak_lanjut`
- [x] Jam operasional TimeField; tanpa upload logo
- [x] Dashboard petugas
