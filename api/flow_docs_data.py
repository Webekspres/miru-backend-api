"""Flow-based API documentation data for MIRU Bank Sampah."""

import json

META = {
    'timestamp': '2026-07-07T14:30:00+09:00',
    'request_id': 'req_demo_001',
}


def _meta(**extra):
    return {**META, **extra}


def _envelope(data, message, status_code=200, success=True, code=None, errors=None, **meta_extra):
    body = {
        'success': success,
        'status_code': status_code,
        'message': message,
        'data': data,
        'meta': _meta(**meta_extra),
    }
    if not success:
        body['code'] = code
        body['errors'] = errors
    return body


def _json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)


DEMO_USERS = [
    {
        'role': 'nasabah',
        'username': 'nasabah001',
        'password': 'nasabah123',
        'nama_lengkap': 'Nasabah Satu',
        'keterangan': 'Akun nasabah untuk uji setoran, penjemputan, penarikan, dan penukaran poin.',
    },
    {
        'role': 'petugas',
        'username': 'petugas1',
        'password': 'petugas123',
        'nama_lengkap': 'Petugas Satu',
        'keterangan': 'Petugas lapangan — mencatat setoran sampah dari nasabah.',
    },
    {
        'role': 'koordinator',
        'username': 'koordinator',
        'password': 'koordinator123',
        'nama_lengkap': 'Arfan Koordinator',
        'keterangan': 'Koordinator — kelola kategori, lihat laporan, setujui penarikan.',
    },
    {
        'role': 'admin',
        'username': 'admin',
        'password': 'admin123',
        'nama_lengkap': 'Harorld Sopacua',
        'keterangan': 'Admin penuh — kelola user, mitra, penjualan, dan semua transaksi.',
    },
]


FLOW_SECTIONS = [
    {
        'id': 'intro',
        'group': 'Pengenalan',
        'title': 'Format Response API',
        'demo_user': None,
        'description': (
            'Semua endpoint API (kecuali schema OpenAPI) mengembalikan JSON Envelope '
            'dengan struktur konsisten. Jalankan seed data terlebih dahulu: '
            '<code>python manage.py seed_data --flush</code>'
        ),
        'endpoints': [],
        'extra_blocks': [
            {
                'title': 'Struktur Envelope',
                'content': _json(_envelope(
                    {'contoh': 'payload di sini'},
                    'Pesan human-readable dalam Bahasa Indonesia.',
                )),
            },
        ],
    },
    {
        'id': 'demo-users',
        'group': 'Pengenalan',
        'title': 'Akun Demo per Role',
        'demo_user': None,
        'description': 'Gunakan akun berikut setelah menjalankan <code>seed_data</code>. Satu akun per role untuk memahami alur.',
        'endpoints': [],
        'show_demo_users': True,
    },
    {
        'id': 'health',
        'group': '01 · Persiapan',
        'title': 'Health Check',
        'demo_user': None,
        'description': 'Langkah pertama — pastikan server berjalan sebelum memanggil API lainnya.',
        'endpoints': [
            {
                'method': 'GET',
                'path': '/health/',
                'auth': 'Public',
                'description': 'Cek status server. Tidak memerlukan token.',
                'request_headers': 'Accept: application/json',
                'request_body': None,
                'response': _json(_envelope(
                    {'status': 'ok'},
                    'Server berjalan normal.',
                )),
            },
        ],
    },
    {
        'id': 'login',
        'group': '02 · Autentikasi',
        'title': 'Login',
        'demo_user': 'nasabah',
        'description': (
            'Mulai dari sini untuk semua flow berikutnya. Response berisi <code>access</code> '
            'dan <code>refresh</code> token JWT, plus profil singkat user.'
        ),
        'endpoints': [
            {
                'method': 'POST',
                'path': '/api/auth/login/',
                'auth': 'Public',
                'description': 'Login dengan username dan password. Gunakan akun demo sesuai role yang ingin diuji.',
                'request_headers': 'Content-Type: application/json',
                'request_body': _json({
                    'username': 'nasabah001',
                    'password': 'nasabah123',
                }),
                'response': _json(_envelope(
                    {
                        'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                        'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                        'user': {
                            'id': 5,
                            'username': 'nasabah001',
                            'role': 'nasabah',
                            'nama_lengkap': 'Nasabah Satu',
                            'no_hp': '08120000001',
                            'saldo': '125000.00',
                            'poin': 125,
                        },
                    },
                    'Login berhasil.',
                )),
                'response_error': _json(_envelope(
                    None,
                    'Username atau password salah.',
                    status_code=401,
                    success=False,
                    code='AUTHENTICATION_FAILED',
                    errors=None,
                )),
            },
        ],
    },
    {
        'id': 'refresh',
        'group': '02 · Autentikasi',
        'title': 'Refresh Token',
        'demo_user': 'nasabah',
        'description': 'Perbarui access token saat kedaluwarsa tanpa login ulang.',
        'endpoints': [
            {
                'method': 'POST',
                'path': '/api/auth/refresh/',
                'auth': 'Public',
                'description': 'Kirim refresh token dari response login.',
                'request_headers': 'Content-Type: application/json',
                'request_body': _json({
                    'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                }),
                'response': _json(_envelope(
                    {'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'},
                    'Token berhasil diperbarui.',
                )),
            },
        ],
    },
    {
        'id': 'me',
        'group': '02 · Autentikasi',
        'title': 'Profil Saya',
        'demo_user': 'nasabah',
        'description': 'Ambil atau perbarui profil user yang sedang login. Nasabah tidak bisa mengubah role, saldo, atau poin.',
        'endpoints': [
            {
                'method': 'GET',
                'path': '/api/auth/me/',
                'auth': 'JWT',
                'description': 'Profil lengkap user login.',
                'request_headers': 'Authorization: Bearer <access_token>',
                'request_body': None,
                'response': _json(_envelope(
                    {
                        'id': 5,
                        'username': 'nasabah001',
                        'role': 'nasabah',
                        'nama_lengkap': 'Nasabah Satu',
                        'no_hp': '08120000001',
                        'alamat': 'Jl. Cendrawasih, Timika',
                        'saldo': '125000.00',
                        'poin': 125,
                        'is_active': True,
                        'date_joined': '2026-07-01T08:00:00+09:00',
                    },
                    'Profil berhasil diambil.',
                )),
            },
            {
                'method': 'PATCH',
                'path': '/api/auth/me/',
                'auth': 'JWT',
                'description': 'Perbarui profil (nama, no HP, alamat).',
                'request_headers': 'Authorization: Bearer <access_token>\nContent-Type: application/json',
                'request_body': _json({
                    'nama_lengkap': 'Nasabah Satu (Diperbarui)',
                    'no_hp': '08129999001',
                }),
                'response': _json(_envelope(
                    {
                        'id': 5,
                        'username': 'nasabah001',
                        'role': 'nasabah',
                        'nama_lengkap': 'Nasabah Satu (Diperbarui)',
                        'no_hp': '08129999001',
                        'saldo': '125000.00',
                        'poin': 125,
                    },
                    'Profil berhasil diperbarui.',
                )),
            },
        ],
    },
    {
        'id': 'register',
        'group': '03 · Registrasi',
        'title': 'Daftar Nasabah Baru',
        'demo_user': None,
        'description': 'Registrasi publik — hanya membuat akun dengan role <code>nasabah</code>. Saldo dan poin awal = 0.',
        'endpoints': [
            {
                'method': 'POST',
                'path': '/api/users/',
                'auth': 'Public',
                'description': 'Buat akun nasabah baru.',
                'request_headers': 'Content-Type: application/json',
                'request_body': _json({
                    'username': 'budi_santoso',
                    'password': 'rahasia123',
                    'nama_lengkap': 'Budi Santoso',
                    'no_hp': '08123456789',
                    'alamat': 'Jl. Cendrawasih No. 1, Timika',
                }),
                'response': _json(_envelope(
                    {
                        'id': 200,
                        'username': 'budi_santoso',
                        'role': 'nasabah',
                        'nama_lengkap': 'Budi Santoso',
                        'saldo': '0.00',
                        'poin': 0,
                        'is_active': True,
                    },
                    'Registrasi nasabah berhasil.',
                    status_code=201,
                )),
            },
        ],
    },
    {
        'id': 'waste-categories',
        'group': '04 · Data Referensi',
        'title': 'Kategori Sampah',
        'demo_user': None,
        'description': 'Data referensi harga sampah. Endpoint list/detail bersifat public (tanpa login).',
        'endpoints': [
            {
                'method': 'GET',
                'path': '/api/waste-categories/',
                'auth': 'Public',
                'description': 'Daftar 8 kategori sampah beserta harga beli per kg.',
                'request_headers': 'Accept: application/json',
                'request_body': None,
                'response': _json(_envelope(
                    [
                        {
                            'id': 1,
                            'nama': 'Plastik PET',
                            'harga_beli_per_kg': '3000.00',
                            'stok_terkini_kg': '150.50',
                        },
                        {
                            'id': 2,
                            'nama': 'Gelas Plastik',
                            'harga_beli_per_kg': '4000.00',
                            'stok_terkini_kg': '75.00',
                        },
                    ],
                    'Daftar kategorisampah berhasil diambil.',
                    **{'pagination': {
                        'count': 8, 'page': 1, 'page_size': 20,
                        'total_pages': 1, 'next': None, 'previous': None,
                    }},
                )),
            },
            {
                'method': 'POST',
                'path': '/api/waste-categories/',
                'auth': 'JWT (admin/koordinator)',
                'description': 'Tambah kategori baru — hanya admin atau koordinator.',
                'request_headers': 'Authorization: Bearer <access_token_admin>\nContent-Type: application/json',
                'request_body': _json({
                    'nama': 'Plastik HDPE',
                    'harga_beli_per_kg': '3500.00',
                }),
                'response': _json(_envelope(
                    {
                        'id': 9,
                        'nama': 'Plastik HDPE',
                        'harga_beli_per_kg': '3500.00',
                        'stok_terkini_kg': '0.00',
                    },
                    'Kategorisampah berhasil dibuat.',
                    status_code=201,
                )),
                'demo_user': 'admin',
            },
        ],
    },
    {
        'id': 'rewards',
        'group': '04 · Data Referensi',
        'title': 'Katalog Reward',
        'demo_user': None,
        'description': 'Daftar reward yang bisa ditukar dengan poin. List bersifat public.',
        'endpoints': [
            {
                'method': 'GET',
                'path': '/api/rewards/',
                'auth': 'Public',
                'description': 'Lihat katalog reward dan poin yang dibutuhkan.',
                'request_headers': 'Accept: application/json',
                'request_body': None,
                'response': _json(_envelope(
                    [
                        {'id': 1, 'nama': 'Pulsa Rp10.000', 'poin_dibutuhkan': 100, 'stok': 50},
                        {'id': 2, 'nama': 'Bibit Tanaman', 'poin_dibutuhkan': 50, 'stok': 30},
                    ],
                    'Daftar rewards berhasil diambil.',
                )),
            },
        ],
    },
    {
        'id': 'pickup',
        'group': '05 · Flow Nasabah',
        'title': 'Ajukan Penjemputan',
        'demo_user': 'nasabah',
        'description': (
            'Nasabah mengajukan penjemputan sampah dari rumah. '
            'Status awal: <code>menunggu</code> — menunggu persetujuan admin.'
        ),
        'endpoints': [
            {
                'method': 'POST',
                'path': '/api/pickups/',
                'auth': 'JWT (nasabah)',
                'description': 'Ajukan permintaan penjemputan.',
                'request_headers': 'Authorization: Bearer <access_token_nasabah>\nContent-Type: application/json',
                'request_body': _json({
                    'estimasi_berat': '8.00',
                    'alamat_jemput': 'Jl. Cendrawasih Poros SP.II, Timika',
                    'jadwal': '2026-07-08T09:00:00+09:00',
                    'catatan': 'Sampah sudah dipilah di depan rumah',
                }),
                'response': _json(_envelope(
                    {
                        'id': 10,
                        'nasabah': 5,
                        'petugas': None,
                        'estimasi_berat': '8.00',
                        'alamat_jemput': 'Jl. Cendrawasih Poros SP.II, Timika',
                        'jadwal': '2026-07-08T09:00:00+09:00',
                        'status': 'menunggu',
                        'catatan': 'Sampah sudah dipilah di depan rumah',
                    },
                    'Penjemputan berhasil dibuat.',
                    status_code=201,
                )),
            },
            {
                'method': 'GET',
                'path': '/api/pickups/',
                'auth': 'JWT',
                'description': 'Lihat riwayat penjemputan (nasabah hanya milik sendiri).',
                'request_headers': 'Authorization: Bearer <access_token_nasabah>',
                'request_body': None,
                'response': _json(_envelope(
                    [{'id': 10, 'status': 'menunggu', 'estimasi_berat': '8.00'}],
                    'Daftar penjemputans berhasil diambil.',
                )),
            },
        ],
    },
    {
        'id': 'withdrawal',
        'group': '05 · Flow Nasabah',
        'title': 'Ajukan Penarikan Saldo',
        'demo_user': 'nasabah',
        'description': 'Nasabah menarik saldo tunai. Minimal penarikan Rp50.000. Status awal: <code>menunggu</code>.',
        'endpoints': [
            {
                'method': 'POST',
                'path': '/api/withdrawals/',
                'auth': 'JWT (nasabah)',
                'description': 'Ajukan penarikan saldo.',
                'request_headers': 'Authorization: Bearer <access_token_nasabah>\nContent-Type: application/json',
                'request_body': _json({
                    'nominal': '100000.00',
                    'metode': 'tunai',
                }),
                'response': _json(_envelope(
                    {
                        'id': 7,
                        'nasabah': 5,
                        'nominal': '100000.00',
                        'metode': 'tunai',
                        'status': 'menunggu',
                    },
                    'Penarikan berhasil dibuat.',
                    status_code=201,
                )),
            },
        ],
    },
    {
        'id': 'redemption',
        'group': '05 · Flow Nasabah',
        'title': 'Tukar Poin Reward',
        'demo_user': 'nasabah',
        'description': 'Nasabah menukar poin dengan reward dari katalog. Poin dipotong saat admin menyetujui.',
        'endpoints': [
            {
                'method': 'POST',
                'path': '/api/reward-redemptions/',
                'auth': 'JWT (nasabah)',
                'description': 'Ajukan penukaran poin.',
                'request_headers': 'Authorization: Bearer <access_token_nasabah>\nContent-Type: application/json',
                'request_body': _json({'reward': 1}),
                'response': _json(_envelope(
                    {
                        'id': 3,
                        'nasabah': 5,
                        'reward': 1,
                        'poin_dibutuhkan': 100,
                        'status': 'menunggu',
                    },
                    'Penukaranpoin berhasil dibuat.',
                    status_code=201,
                )),
            },
        ],
    },
    {
        'id': 'complaint',
        'group': '05 · Flow Nasabah',
        'title': 'Kirim Pengaduan',
        'demo_user': 'nasabah',
        'description': 'Nasabah melaporkan masalah terkait layanan bank sampah.',
        'endpoints': [
            {
                'method': 'POST',
                'path': '/api/complaints/',
                'auth': 'JWT (nasabah)',
                'description': 'Buat pengaduan baru.',
                'request_headers': 'Authorization: Bearer <access_token_nasabah>\nContent-Type: application/json',
                'request_body': _json({
                    'jenis_pengaduan': 'saldo_belum_masuk',
                    'isi_pengaduan': 'Setoran kemarin belum masuk ke saldo saya.',
                }),
                'response': _json(_envelope(
                    {
                        'id': 4,
                        'nasabah': 5,
                        'jenis_pengaduan': 'saldo_belum_masuk',
                        'isi_pengaduan': 'Setoran kemarin belum masuk ke saldo saya.',
                        'status': 'terbuka',
                    },
                    'Pengaduan berhasil dibuat.',
                    status_code=201,
                )),
            },
        ],
    },
    {
        'id': 'deposit',
        'group': '06 · Flow Petugas',
        'title': 'Catat Setoran Sampah',
        'demo_user': 'petugas',
        'description': (
            'Alur inti bank sampah. Petugas mencatat setoran nasabah — '
            'saldo dan poin nasabah bertambah otomatis, stok kategori juga bertambah.'
        ),
        'flow_diagram': 'nasabah bawa sampah → petugas timbang → POST /api/deposits/ → saldo & poin naik',
        'endpoints': [
            {
                'method': 'POST',
                'path': '/api/deposits/',
                'auth': 'JWT (petugas/admin)',
                'description': (
                    'Catat transaksi setoran. Field <code>petugas</code> diisi otomatis dari user login. '
                    'Minimal 1 kg per jenis sampah.'
                ),
                'request_headers': 'Authorization: Bearer <access_token_petugas>\nContent-Type: application/json',
                'request_body': _json({
                    'nasabah': 5,
                    'details': [
                        {'kategori': 1, 'berat_kg': '5.00'},
                        {'kategori': 3, 'berat_kg': '3.50'},
                    ],
                }),
                'response': _json(_envelope(
                    {
                        'id': 42,
                        'nasabah': 5,
                        'petugas': 3,
                        'tanggal': '2026-07-07T10:30:00+09:00',
                        'total_nilai': '20250.00',
                        'status': 'selesai',
                        'details': [
                            {
                                'id': 80,
                                'kategori': 1,
                                'kategori_nama': 'Plastik PET',
                                'berat_kg': '5.00',
                                'harga_saat_itu': '3000.00',
                                'subtotal': '15000.00',
                            },
                            {
                                'id': 81,
                                'kategori': 3,
                                'kategori_nama': 'Kardus',
                                'berat_kg': '3.50',
                                'harga_saat_itu': '1500.00',
                                'subtotal': '5250.00',
                            },
                        ],
                    },
                    'Transaksisetoran berhasil dibuat.',
                    status_code=201,
                )),
            },
            {
                'method': 'GET',
                'path': '/api/deposits/?nasabah=5',
                'auth': 'JWT',
                'description': 'Lihat riwayat setoran nasabah tertentu.',
                'request_headers': 'Authorization: Bearer <access_token_petugas>',
                'request_body': None,
                'response': _json(_envelope(
                    [{'id': 42, 'nasabah': 5, 'total_nilai': '20250.00', 'status': 'selesai'}],
                    'Daftar transaksisetorans berhasil diambil.',
                )),
            },
        ],
    },
    {
        'id': 'admin-users',
        'group': '07 · Flow Admin & Koordinator',
        'title': 'Kelola Pengguna',
        'demo_user': 'admin',
        'description': 'Admin membuat akun petugas/koordinator dan mengelola daftar user.',
        'endpoints': [
            {
                'method': 'GET',
                'path': '/api/users/?role=nasabah&search=nasabah',
                'auth': 'JWT (admin/koordinator)',
                'description': 'Cari dan filter daftar user.',
                'request_headers': 'Authorization: Bearer <access_token_admin>',
                'request_body': None,
                'response': _json(_envelope(
                    [
                        {
                            'id': 5,
                            'username': 'nasabah001',
                            'role': 'nasabah',
                            'nama_lengkap': 'Nasabah Satu',
                            'saldo': '125000.00',
                            'poin': 125,
                        },
                    ],
                    'Daftar users berhasil diambil.',
                )),
            },
            {
                'method': 'POST',
                'path': '/api/users/',
                'auth': 'JWT (admin)',
                'description': 'Buat akun petugas baru (bukan registrasi publik).',
                'request_headers': 'Authorization: Bearer <access_token_admin>\nContent-Type: application/json',
                'request_body': _json({
                    'username': 'petugas_baru',
                    'password': 'petugas123',
                    'role': 'petugas',
                    'nama_lengkap': 'Petugas Baru',
                    'no_hp': '08130000001',
                }),
                'response': _json(_envelope(
                    {
                        'id': 10,
                        'username': 'petugas_baru',
                        'role': 'petugas',
                        'nama_lengkap': 'Petugas Baru',
                    },
                    'User berhasil dibuat.',
                    status_code=201,
                )),
            },
        ],
    },
    {
        'id': 'admin-withdrawal',
        'group': '07 · Flow Admin & Koordinator',
        'title': 'Setujui Penarikan Saldo',
        'demo_user': 'koordinator',
        'description': (
            'Admin/koordinator menyetujui penarikan yang diajukan nasabah. '
            'Saldo nasabah berkurang saat status diubah ke <code>selesai</code>.'
        ),
        'endpoints': [
            {
                'method': 'GET',
                'path': '/api/withdrawals/?status=menunggu',
                'auth': 'JWT (admin/koordinator)',
                'description': 'Lihat daftar penarikan yang menunggu persetujuan.',
                'request_headers': 'Authorization: Bearer <access_token_koordinator>',
                'request_body': None,
                'response': _json(_envelope(
                    [{'id': 7, 'nasabah': 5, 'nominal': '100000.00', 'status': 'menunggu'}],
                    'Daftar penarikans berhasil diambil.',
                )),
            },
            {
                'method': 'PATCH',
                'path': '/api/withdrawals/7/',
                'auth': 'JWT (admin/koordinator)',
                'description': 'Ubah status penarikan menjadi selesai setelah pembayaran tunai.',
                'request_headers': 'Authorization: Bearer <access_token_koordinator>\nContent-Type: application/json',
                'request_body': _json({'status': 'selesai'}),
                'response': _json(_envelope(
                    {'id': 7, 'status': 'selesai', 'nominal': '100000.00'},
                    'Penarikan berhasil diperbarui.',
                )),
            },
        ],
    },
    {
        'id': 'admin-pickup',
        'group': '07 · Flow Admin & Koordinator',
        'title': 'Kelola Penjemputan',
        'demo_user': 'admin',
        'description': (
            'Admin menugaskan petugas dan mengubah status penjemputan. '
            'Alur status: <code>menunggu → disetujui → dijadwalkan → dijemput → selesai</code>'
        ),
        'endpoints': [
            {
                'method': 'PATCH',
                'path': '/api/pickups/10/',
                'auth': 'JWT (admin/petugas)',
                'description': 'Tugaskan petugas dan ubah status penjemputan.',
                'request_headers': 'Authorization: Bearer <access_token_admin>\nContent-Type: application/json',
                'request_body': _json({
                    'petugas': 3,
                    'status': 'dijadwalkan',
                    'jadwal': '2026-07-08T09:00:00+09:00',
                }),
                'response': _json(_envelope(
                    {
                        'id': 10,
                        'petugas': 3,
                        'status': 'dijadwalkan',
                        'jadwal': '2026-07-08T09:00:00+09:00',
                    },
                    'Penjemputan berhasil diperbarui.',
                )),
            },
        ],
    },
    {
        'id': 'admin-redemption',
        'group': '07 · Flow Admin & Koordinator',
        'title': 'Setujui Penukaran Poin',
        'demo_user': 'admin',
        'description': 'Admin menyetujui penukaran poin — poin nasabah berkurang saat status <code>selesai</code>.',
        'endpoints': [
            {
                'method': 'PATCH',
                'path': '/api/reward-redemptions/3/',
                'auth': 'JWT (admin)',
                'description': 'Setujui penukaran poin.',
                'request_headers': 'Authorization: Bearer <access_token_admin>\nContent-Type: application/json',
                'request_body': _json({'status': 'selesai'}),
                'response': _json(_envelope(
                    {'id': 3, 'status': 'selesai', 'poin_dibutuhkan': 100},
                    'Penukaranpoin berhasil diperbarui.',
                )),
            },
        ],
    },
    {
        'id': 'partners',
        'group': '07 · Flow Admin & Koordinator',
        'title': 'Mitra & Penjualan',
        'demo_user': 'admin',
        'description': 'Admin mengelola mitra pengepul dan mencatat penjualan stok sampah ke mitra.',
        'endpoints': [
            {
                'method': 'GET',
                'path': '/api/partners/',
                'auth': 'JWT (admin/koordinator)',
                'description': 'Daftar mitra pengepul.',
                'request_headers': 'Authorization: Bearer <access_token_admin>',
                'request_body': None,
                'response': _json(_envelope(
                    [
                        {
                            'id': 1,
                            'nama': 'PT Pengepul Timika',
                            'kontak': '08120001111',
                            'alamat': 'Timika',
                        },
                    ],
                    'Daftar partners berhasil diambil.',
                )),
            },
            {
                'method': 'POST',
                'path': '/api/partner-sales/',
                'auth': 'JWT (admin)',
                'description': 'Catat penjualan stok ke mitra — stok kategori berkurang otomatis.',
                'request_headers': 'Authorization: Bearer <access_token_admin>\nContent-Type: application/json',
                'request_body': _json({
                    'mitra': 1,
                    'kategori': 1,
                    'berat_jual_kg': '100.00',
                    'harga_jual_per_kg': '2500.00',
                }),
                'response': _json(_envelope(
                    {
                        'id': 5,
                        'mitra': 1,
                        'kategori': 1,
                        'berat_jual_kg': '100.00',
                        'harga_jual_per_kg': '2500.00',
                        'total_nilai': '250000.00',
                    },
                    'Penjualanmitra berhasil dibuat.',
                    status_code=201,
                )),
            },
        ],
    },
]


def get_demo_user(role_key):
    mapping = {u['role']: u for u in DEMO_USERS}
    return mapping.get(role_key)


def get_nav_groups():
    groups = []
    seen = set()
    for section in FLOW_SECTIONS:
        g = section['group']
        if g not in seen:
            seen.add(g)
            items = [
                {'id': s['id'], 'title': s['title']}
                for s in FLOW_SECTIONS
                if s['group'] == g
            ]
            groups.append({'name': g, 'items': items})
    return groups
