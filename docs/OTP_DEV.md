# OTP Development Mode (`OTP_DEV_FIXED_CODE`)

Gunakan ini saat **local / development** tanpa kredensial WhatsApp Business API, supaya alur verifikasi HP dan lupa password tetap bisa diuji di mobile/web.

## Masalah yang diselesaikan

Setelah login, akun dengan `phone_verified=false` diarahkan ke layar OTP WhatsApp. Jika `WA_*` belum diisi, backend **stub** pengiriman (sukses palsu) tetapi **tidak** melog atau mengembalikan kode OTP — developer tidak punya kode untuk dimasukkan.

## Cara aktifkan

1. Di `.env` backend (lihat `.env.example`):

```env
DEBUG=True
OTP_DEV_FIXED_CODE=123456
```

2. **Restart wajib** `runserver` / container web setelah mengubah `.env`  
   (Django **tidak** me-reload saat hanya `.env` yang berubah — hanya file `.py`).
3. Di layar OTP, tekan **Kirim ulang OTP** (supaya hash di DB memakai kode baru).
4. Masukkan kode tetap yang sama (`123456` di contoh di atas).

Jika Anda mengganti `OTP_DEV_FIXED_CODE` (mis. `123456` → `424242`) tanpa restart + kirim ulang, verifikasi akan gagal: OTP aktif di DB masih kode lama/acak.

Respons API request-OTP (hanya saat mode ini aktif) berisi:

| Field | Arti |
|-------|------|
| `dev_otp` | Kode yang harus dimasukkan |
| `dev_otp_mode` | `true` |
| `message` | Teks yang menyebut mode development + kode |

Contoh cuplikan:

```json
{
  "success": true,
  "data": {
    "masked_phone": "081****89",
    "expires_in_seconds": 300,
    "dev_otp": "123456",
    "dev_otp_mode": true
  },
  "message": "Mode development: gunakan OTP tetap 123456 (tidak dikirim WhatsApp nyata)."
}
```

SnackBar di mobile menampilkan `message` — kode terlihat di UI tanpa membuka log server.

## Syarat keamanan (wajib)

Mode OTP tetap **hanya** aktif jika **semua** benar:

1. `DEBUG=True`
2. `OTP_DEV_FIXED_CODE` berisi **tepat 6 digit** numerik

Jika `DEBUG=False` (production), env `OTP_DEV_FIXED_CODE` **diabaikan** meskipun terisi. Jangan mengandalkan “hapus env saja” — pastikan production selalu `DEBUG=False`.

Kode OTP **tidak** ditulis ke log aplikasi (tetap sesuai kebijakan “jangan log OTP”).

## Endpoint yang terpengaruh

| Endpoint | Peran |
|----------|--------|
| `POST /api/auth/phone/request-otp/` | Verifikasi HP / registrasi |
| `POST /api/auth/reset-password/request-otp/` | Lupa password |

Verifikasi tetap lewat `verify-otp` seperti biasa; hanya **sumber kode** yang diganti (acak → tetap).

## Urutan pemilihan kode

1. Argumen `code=` di `create_and_send_otp` (suite test)
2. `OTP_DEV_FIXED_CODE` jika mode dev aktif
3. Kode acak 6 digit

## Production / staging dengan WA nyata

1. Set `DEBUG=False` di production.
2. Isi `WA_API_URL` + `WA_API_TOKEN` (+ `WA_SENDER` bila perlu).
3. Biarkan `OTP_DEV_FIXED_CODE` kosong atau hapus dari env production.

Tanpa `WA_*`, pengiriman tetap stub; tanpa `OTP_DEV_FIXED_CODE` + `DEBUG`, developer harus set `phone_verified=True` manual atau inject OTP lewat Django shell (lihat catatan di bawah).

## Alternatif cepat tanpa OTP tetap

```python
# manage.py shell
from api.models import User
User.objects.filter(username='nasabah001').update(phone_verified=True)
```

Atau inject satu kode:

```python
from api.models import User
from api.services.whatsapp import create_and_send_otp

u = User.objects.get(username='nasabah001')
create_and_send_otp(u, 'phone_verify', u.no_hp, code='123456')
```

## Kaitan proposal / modul

- **Modul 2 (Autentikasi):** verifikasi nomor tetap ada di production path.
- **WhatsApp/SMS** di proposal adalah layanan pihak ketiga opsional; stub + OTP tetap hanya alat DX, bukan perilaku go-live.
- Lihat juga `.ai-steering/10-security-and-privacy.md` (secrets di env, jangan log OTP/PII).
