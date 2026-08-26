"""OpenAPI / drf-spectacular configuration helpers."""

from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

from .serializers import NotifikasiSerializer, UserProfileSerializer

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
ACTIVITY_TAG = 'Activity'
DASHBOARD_TAG = 'Dashboard'
REPORTS_TAG = 'Reports'
AUDIT_LOG_TAG = 'Audit Log'
INVENTORY_TAG = 'Inventory'
EDUKASI_TAG = 'Edukasi'
MEDIA_TAG = 'Media'
NOTIFICATIONS_TAG = 'Notifications'
SETTINGS_TAG = 'Settings'


def _query_param(name, schema_type='string', required=False, description=''):
    return {
        'name': name,
        'in': 'query',
        'required': required,
        'schema': {'type': schema_type},
        'description': description,
    }


dashboard_overview_schema = extend_schema(
    tags=[DASHBOARD_TAG],
    summary='Ringkasan monitoring (admin/koordinator/pemerintah) atau widget petugas',
    description=(
        'Admin/koordinator/pemerintah: data agregat (total nasabah, nasabah aktif '
        '30 hari, total sampah & nilai setoran, penarikan, penukaran poin, '
        'penjemputan menunggu, pengaduan terbuka, stok per kategori).\n\n'
        'Petugas: widget ringkas — jemput_ditugaskan_hari_ini dan antrian_aktif '
        '(hanya tugas milik sendiri).'
    ),
)

dashboard_deposit_chart_schema = extend_schema(
    tags=[DASHBOARD_TAG],
    summary='Data setoran harian untuk chart',
    description='Total nilai, berat, dan jumlah transaksi per hari untuk satu bulan.',
    parameters=[
        _query_param('bulan', 'integer', description='Bulan 1-12 (default: bulan berjalan)'),
        _query_param('tahun', 'integer', description='Tahun (default: tahun berjalan)'),
    ],
)

dashboard_recent_activity_schema = extend_schema(
    tags=[DASHBOARD_TAG],
    summary='Aktivitas transaksi terbaru',
    description='Gabungan setoran, penarikan, dan penjemputan terbaru, urut waktu.',
    parameters=[
        _query_param('limit', 'integer', description='Jumlah item (1-50, default 10)'),
    ],
)

report_daily_schema = extend_schema(
    tags=[REPORTS_TAG],
    summary='Laporan harian',
    parameters=[_query_param('tanggal', 'string', required=True, description='Format YYYY-MM-DD')],
)

report_weekly_schema = extend_schema(
    tags=[REPORTS_TAG],
    summary='Laporan mingguan (nomor minggu ISO)',
    parameters=[
        _query_param('minggu', 'integer', description='Nomor minggu ISO 1-53 (default: minggu berjalan)'),
        _query_param('tahun', 'integer', description='Tahun (default: tahun berjalan)'),
    ],
)

report_monthly_schema = extend_schema(
    tags=[REPORTS_TAG],
    summary='Laporan bulanan lengkap (format SOP)',
    parameters=[
        _query_param('bulan', 'integer', description='Bulan 1-12 (default: bulan berjalan)'),
        _query_param('tahun', 'integer', description='Tahun (default: tahun berjalan)'),
    ],
)

report_waste_schema = extend_schema(
    tags=[REPORTS_TAG],
    summary='Laporan tonase & nilai sampah per kategori',
    parameters=[
        _query_param('start', 'string', required=True, description='Format YYYY-MM-DD'),
        _query_param('end', 'string', required=True, description='Format YYYY-MM-DD'),
    ],
)

report_evaluation_schema = extend_schema(
    tags=[REPORTS_TAG],
    summary='Data agregat evaluasi program',
    parameters=[
        _query_param('start', 'string', required=True, description='Format YYYY-MM-DD'),
        _query_param('end', 'string', required=True, description='Format YYYY-MM-DD'),
    ],
)

inventory_schema = extend_schema(
    tags=[INVENTORY_TAG],
    summary='Ringkasan stok gudang semua kategori',
)

inventory_history_schema = extend_schema(
    tags=[INVENTORY_TAG],
    summary='Riwayat perubahan stok per kategori',
    description=(
        'Gabungan pergerakan stok dari setoran (masuk) dan penjualan ke mitra (keluar), '
        'diurutkan terbaru dulu.'
    ),
    parameters=[
        _query_param('limit', 'integer', description='Jumlah item (1-100, default 50)'),
    ],
)

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
    description=(
        'Ambil profil lengkap user dari JWT. Termasuk field `qr` '
        '({ id, nama_lengkap, no_hp }) untuk kartu digital. '
        'Nasabah tidak bisa ubah role/saldo/poin via PATCH.'
    ),
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
                    'setuju_kebijakan_data': True,
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
    partial_update=extend_schema(
        summary='Koreksi data setoran (admin only)',
        description=(
            'Admin dapat mengoreksi total_nilai transaksi. '
            'Perubahan saldo/poin nasabah disesuaikan otomatis dan tercatat di audit log.'
        ),
        tags=[DEPOSITS_TAG],
    ),
    update=extend_schema(summary='Koreksi data setoran (admin only)', tags=[DEPOSITS_TAG]),
    destroy=extend_schema(exclude=True),
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

settings_schema = extend_schema_view(
    get=extend_schema(
        tags=[SETTINGS_TAG],
        summary='Pengaturan institusi (public)',
        description='Profil institusi untuk tampilan mobile dan web.',
    ),
)

pengumuman_list_schema = extend_schema(
    tags=[SETTINGS_TAG],
    summary='Daftar pengumuman aktif (public)',
    description='Pengumuman yang ditampilkan di aplikasi mobile nasabah.',
)


edukasi_schema = extend_schema_view(
    list=extend_schema(
        summary='Daftar konten edukasi (public)',
        tags=[EDUKASI_TAG],
        description='Konten edukasi sampah — artikel/panduan untuk nasabah. List public (tanpa auth).',
    ),
    retrieve=extend_schema(
        summary='Detail konten edukasi (public)',
        tags=[EDUKASI_TAG],
    ),
    create=extend_schema(
        summary='Tambah konten edukasi (admin/koordinator)',
        tags=[EDUKASI_TAG],
        examples=[
            OpenApiExample(
                'Buat artikel edukasi',
                value={
                    'judul': 'Cara Memilah Sampah yang Benar',
                    'isi': 'Panduan lengkap memilah sampah rumah tangga...',
                    'gambar_url': 'edukasi/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.webp',
                    'kategori_terkait': 1,
                    'aktif': True,
                },
                request_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(summary='Perbarui konten edukasi', tags=[EDUKASI_TAG]),
    update=extend_schema(summary='Perbarui konten edukasi', tags=[EDUKASI_TAG]),
    destroy=extend_schema(summary='Hapus konten edukasi (admin only)', tags=[EDUKASI_TAG]),
)


# ── Excel Export schemas (Fase 8.6) ──────────────────────────


def _export_schema(summary: str, description: str, parameters: list) -> extend_schema:
    return extend_schema(
        tags=[REPORTS_TAG],
        summary=summary,
        description=description,
        parameters=parameters,
        responses={
            200: {
                'type': 'string',
                'format': 'binary',
                'description': 'Excel file (.xlsx)',
            },
        },
    )


export_daily_schema = _export_schema(
    'Export laporan harian ke Excel (.xlsx)',
    'Download laporan harian dalam format Excel.',
    parameters=[_query_param('tanggal', 'string', required=True, description='Format YYYY-MM-DD')],
)

export_weekly_schema = _export_schema(
    'Export laporan mingguan ke Excel (.xlsx)',
    'Download laporan mingguan dalam format Excel.',
    parameters=[
        _query_param('minggu', 'integer', description='Nomor minggu ISO 1-53 (default: minggu berjalan)'),
        _query_param('tahun', 'integer', description='Tahun (default: tahun berjalan)'),
    ],
)

export_monthly_schema = _export_schema(
    'Export laporan bulanan ke Excel (.xlsx)',
    'Download laporan bulanan lengkap format SOP dalam Excel.',
    parameters=[
        _query_param('bulan', 'integer', description='Bulan 1-12 (default: bulan berjalan)'),
        _query_param('tahun', 'integer', description='Tahun (default: tahun berjalan)'),
    ],
)

export_waste_schema = _export_schema(
    'Export laporan sampah ke Excel (.xlsx)',
    'Download laporan tonase & nilai sampah per kategori dalam Excel.',
    parameters=[
        _query_param('start', 'string', required=True, description='Format YYYY-MM-DD'),
        _query_param('end', 'string', required=True, description='Format YYYY-MM-DD'),
    ],
)

export_evaluation_schema = _export_schema(
    'Export laporan evaluasi ke Excel (.xlsx)',
    'Download data agregat evaluasi program dalam format Excel.',
    parameters=[
        _query_param('start', 'string', required=True, description='Format YYYY-MM-DD'),
        _query_param('end', 'string', required=True, description='Format YYYY-MM-DD'),
    ],
)


notification_schema = extend_schema_view(
    list=extend_schema(
        tags=[NOTIFICATIONS_TAG],
        summary='Daftar notifikasi',
        description='Notifikasi in-app untuk user. Nasabah hanya melihat milik sendiri.',
        parameters=[
            {
                'name': 'user',
                'in': 'query',
                'required': False,
                'schema': {'type': 'integer'},
                'description': 'Filter by user ID (staff only)',
            },
        ],
    ),
    retrieve=extend_schema(
        tags=[NOTIFICATIONS_TAG],
        summary='Detail notifikasi',
        responses={200: NotifikasiSerializer},
    ),
    partial_update=extend_schema(
        tags=[NOTIFICATIONS_TAG],
        summary='Perbarui notifikasi (partial)',
        description=(
            'Partial update notifikasi. Untuk menandai sudah dibaca, '
            'utamakan POST /api/notifications/{id}/read/.'
        ),
        responses={200: NotifikasiSerializer},
    ),
    mark_read=extend_schema(
        tags=[NOTIFICATIONS_TAG],
        summary='Tandai satu notifikasi sebagai sudah dibaca',
        description='POST to /notifications/{id}/read/ untuk menandai sudah dibaca.',
        responses={200: NotifikasiSerializer},
    ),
    mark_all_read=extend_schema(
        tags=[NOTIFICATIONS_TAG],
        summary='Tandai semua notifikasi sebagai sudah dibaca',
        description='POST to /notifications/mark-all-read/ untuk menandai semua sudah dibaca.',
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'updated_count': {'type': 'integer'},
                },
            },
        },
    ),
)
