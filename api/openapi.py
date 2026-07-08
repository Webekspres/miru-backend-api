"""OpenAPI / drf-spectacular configuration helpers."""

from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

from .serializers import UserProfileSerializer

DEMO_CREDENTIALS = OpenApiExample(
    'Akun demo (setelah seed_data)',
    value={'username': 'nasabah001', 'password': 'nasabah123'},
    request_only=True,
)

AUTH_TAG = 'Auth'
HEALTH_TAG = 'Health'
USERS_TAG = 'Users'
CATEGORIES_TAG = 'Waste Categories'
DEPOSITS_TAG = 'Deposits'
PICKUPS_TAG = 'Pickups'
WITHDRAWALS_TAG = 'Withdrawals'
REWARDS_TAG = 'Rewards'
REDEMPTIONS_TAG = 'Reward Redemptions'
PARTNERS_TAG = 'Partners'
PARTNER_SALES_TAG = 'Partner Sales'
COMPLAINTS_TAG = 'Complaints'

auth_login_schema = extend_schema(
    tags=[AUTH_TAG],
    summary='Login — dapatkan access & refresh token',
    description=(
        'Autentikasi JWT. Response berisi `access`, `refresh`, dan profil singkat user. '
        'Akun demo: `admin/admin123`, `nasabah001/nasabah123`, `petugas1/petugas123`.'
    ),
    examples=[DEMO_CREDENTIALS],
    auth=[],
)

auth_refresh_schema = extend_schema(
    tags=[AUTH_TAG],
    summary='Refresh access token',
    description='Perbarui access token menggunakan refresh token dari login.',
    auth=[],
)

auth_me_get_schema = extend_schema(
    tags=[AUTH_TAG],
    summary='Profil user yang sedang login',
    description='Ambil profil lengkap user dari JWT. Nasabah tidak bisa ubah role/saldo/poin.',
    responses={200: UserProfileSerializer},
)

auth_me_patch_schema = extend_schema(
    tags=[AUTH_TAG],
    summary='Perbarui profil sendiri',
    description='Update nama, no HP, atau alamat profil user login.',
    request=UserProfileSerializer,
    responses={200: UserProfileSerializer},
)

health_schema = extend_schema(
    tags=[HEALTH_TAG],
    summary='Health check server',
    description='Cek apakah server berjalan. Public, tanpa autentikasi.',
    responses={
        200: {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'status_code': {'type': 'integer'},
                'message': {'type': 'string'},
                'data': {
                    'type': 'object',
                    'properties': {'status': {'type': 'string', 'example': 'ok'}},
                },
            },
        },
    },
)

user_viewset_schema = extend_schema_view(
    list=extend_schema(summary='Daftar pengguna', tags=[USERS_TAG]),
    retrieve=extend_schema(summary='Detail pengguna', tags=[USERS_TAG]),
    create=extend_schema(
        summary='Registrasi nasabah (public) atau buat user staff (admin)',
        tags=[USERS_TAG],
        examples=[
            OpenApiExample(
                'Registrasi nasabah',
                value={
                    'username': 'budi_santoso',
                    'password': 'rahasia123',
                    'nama_lengkap': 'Budi Santoso',
                    'no_hp': '08123456789',
                    'alamat': 'Jl. Cendrawasih, Timika',
                },
                request_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(summary='Perbarui pengguna', tags=[USERS_TAG]),
    update=extend_schema(summary='Perbarui pengguna', tags=[USERS_TAG]),
    destroy=extend_schema(summary='Hapus pengguna', tags=[USERS_TAG]),
)

waste_category_schema = extend_schema_view(
    list=extend_schema(summary='Daftar kategori sampah', tags=[CATEGORIES_TAG]),
    retrieve=extend_schema(summary='Detail kategori sampah', tags=[CATEGORIES_TAG]),
    create=extend_schema(summary='Tambah kategori (admin/koordinator)', tags=[CATEGORIES_TAG]),
    partial_update=extend_schema(summary='Perbarui kategori', tags=[CATEGORIES_TAG]),
    update=extend_schema(summary='Perbarui kategori', tags=[CATEGORIES_TAG]),
    destroy=extend_schema(summary='Hapus kategori', tags=[CATEGORIES_TAG]),
)

deposit_schema = extend_schema_view(
    list=extend_schema(summary='Daftar transaksi setoran', tags=[DEPOSITS_TAG]),
    retrieve=extend_schema(summary='Bukti digital setoran', tags=[DEPOSITS_TAG]),
    create=extend_schema(
        summary='Catat setoran sampah (petugas/admin)',
        tags=[DEPOSITS_TAG],
        examples=[
            OpenApiExample(
                'Setoran nasabah',
                value={
                    'nasabah': 5,
                    'details': [
                        {'kategori': 1, 'berat_kg': '5.00'},
                        {'kategori': 3, 'berat_kg': '3.50'},
                    ],
                },
                request_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(summary='Perbarui setoran', tags=[DEPOSITS_TAG]),
    update=extend_schema(summary='Perbarui setoran', tags=[DEPOSITS_TAG]),
    destroy=extend_schema(summary='Hapus setoran', tags=[DEPOSITS_TAG]),
)

pickup_schema = extend_schema_view(
    list=extend_schema(summary='Daftar penjemputan', tags=[PICKUPS_TAG]),
    retrieve=extend_schema(summary='Detail penjemputan', tags=[PICKUPS_TAG]),
    create=extend_schema(
        summary='Ajukan penjemputan (nasabah)',
        tags=[PICKUPS_TAG],
        examples=[
            OpenApiExample(
                'Ajuan penjemputan',
                value={
                    'estimasi_berat': '8.00',
                    'alamat_jemput': 'Jl. Cendrawasih, Timika',
                    'jadwal': '2026-07-08T09:00:00+09:00',
                    'catatan': 'Sampah sudah dipilah',
                },
                request_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(summary='Perbarui penjemputan', tags=[PICKUPS_TAG]),
    update=extend_schema(summary='Perbarui penjemputan', tags=[PICKUPS_TAG]),
    destroy=extend_schema(summary='Hapus penjemputan', tags=[PICKUPS_TAG]),
)

withdrawal_schema = extend_schema_view(
    list=extend_schema(summary='Daftar penarikan saldo', tags=[WITHDRAWALS_TAG]),
    retrieve=extend_schema(summary='Detail penarikan', tags=[WITHDRAWALS_TAG]),
    create=extend_schema(
        summary='Ajukan penarikan saldo (nasabah)',
        tags=[WITHDRAWALS_TAG],
        examples=[
            OpenApiExample(
                'Penarikan tunai',
                value={'nominal': '100000.00', 'metode': 'tunai'},
                request_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        summary='Setujui / ubah status penarikan (admin/koordinator)',
        tags=[WITHDRAWALS_TAG],
    ),
    update=extend_schema(summary='Ubah penarikan', tags=[WITHDRAWALS_TAG]),
    destroy=extend_schema(summary='Hapus penarikan', tags=[WITHDRAWALS_TAG]),
)

reward_schema = extend_schema_view(
    list=extend_schema(summary='Daftar reward', tags=[REWARDS_TAG]),
    retrieve=extend_schema(summary='Detail reward', tags=[REWARDS_TAG]),
    create=extend_schema(summary='Tambah reward (admin)', tags=[REWARDS_TAG]),
    partial_update=extend_schema(summary='Perbarui reward', tags=[REWARDS_TAG]),
    update=extend_schema(summary='Perbarui reward', tags=[REWARDS_TAG]),
    destroy=extend_schema(summary='Hapus reward', tags=[REWARDS_TAG]),
)

redemption_schema = extend_schema_view(
    list=extend_schema(summary='Daftar penukaran poin', tags=[REDEMPTIONS_TAG]),
    retrieve=extend_schema(summary='Detail penukaran', tags=[REDEMPTIONS_TAG]),
    create=extend_schema(
        summary='Tukar poin dengan reward (nasabah)',
        tags=[REDEMPTIONS_TAG],
        examples=[
            OpenApiExample('Penukaran pulsa', value={'reward': 1}, request_only=True),
        ],
    ),
    partial_update=extend_schema(summary='Setujui penukaran (admin)', tags=[REDEMPTIONS_TAG]),
    update=extend_schema(summary='Ubah penukaran', tags=[REDEMPTIONS_TAG]),
    destroy=extend_schema(summary='Hapus penukaran', tags=[REDEMPTIONS_TAG]),
)

partner_schema = extend_schema_view(
    list=extend_schema(summary='Daftar mitra pengepul', tags=[PARTNERS_TAG]),
    retrieve=extend_schema(summary='Detail mitra', tags=[PARTNERS_TAG]),
    create=extend_schema(summary='Tambah mitra (admin)', tags=[PARTNERS_TAG]),
    partial_update=extend_schema(summary='Perbarui mitra', tags=[PARTNERS_TAG]),
    update=extend_schema(summary='Perbarui mitra', tags=[PARTNERS_TAG]),
    destroy=extend_schema(summary='Hapus mitra', tags=[PARTNERS_TAG]),
)

partner_sale_schema = extend_schema_view(
    list=extend_schema(summary='Daftar penjualan ke mitra', tags=[PARTNER_SALES_TAG]),
    retrieve=extend_schema(summary='Detail penjualan', tags=[PARTNER_SALES_TAG]),
    create=extend_schema(
        summary='Catat penjualan stok ke mitra (admin)',
        tags=[PARTNER_SALES_TAG],
        examples=[
            OpenApiExample(
                'Jual stok PET',
                value={
                    'mitra': 1,
                    'kategori': 1,
                    'berat_jual_kg': '100.00',
                    'harga_jual_per_kg': '2500.00',
                },
                request_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(summary='Perbarui penjualan', tags=[PARTNER_SALES_TAG]),
    update=extend_schema(summary='Perbarui penjualan', tags=[PARTNER_SALES_TAG]),
    destroy=extend_schema(summary='Hapus penjualan', tags=[PARTNER_SALES_TAG]),
)

complaint_schema = extend_schema_view(
    list=extend_schema(summary='Daftar pengaduan', tags=[COMPLAINTS_TAG]),
    retrieve=extend_schema(summary='Detail pengaduan', tags=[COMPLAINTS_TAG]),
    create=extend_schema(
        summary='Kirim pengaduan (nasabah)',
        tags=[COMPLAINTS_TAG],
        examples=[
            OpenApiExample(
                'Pengaduan saldo',
                value={
                    'jenis_pengaduan': 'saldo_belum_masuk',
                    'isi_pengaduan': 'Setoran kemarin belum masuk ke saldo.',
                },
                request_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(summary='Perbarui pengaduan', tags=[COMPLAINTS_TAG]),
    update=extend_schema(summary='Perbarui pengaduan', tags=[COMPLAINTS_TAG]),
    destroy=extend_schema(summary='Hapus pengaduan', tags=[COMPLAINTS_TAG]),
)
