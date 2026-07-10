import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import (
    DetailSetoran,
    KategoriSampah,
    MitraPengepul,
    Notifikasi,
    PenarikanSaldo,
    Penjemputan,
    Pengaduan,
    PengaturanInstitusi,
    Pengumuman,
    PenjualanMitra,
    PenukaranPoin,
    Reward,
    TransaksiSetoran,
    User,
)
from api.notification_signals import connect_notification_signals, disconnect_notification_signals


WASTE_CATEGORIES = [
    ('PET', Decimal('3000.00')),
    ('Gelas Plastik', Decimal('4000.00')),
    ('Kardus', Decimal('1500.00')),
    ('Kertas', Decimal('2000.00')),
    ('Aluminium', Decimal('10000.00')),
    ('Besi', Decimal('3000.00')),
    ('Kaca', Decimal('500.00')),
    ('Jelantah', Decimal('5000.00')),
]

REWARDS = [
    ('Pulsa', 100, 50),
    ('Bibit', 50, 30),
    ('Sembako', 250, 20),
    ('Alat Kebersihan', 300, 15),
]

ADMIN_USER = ('admin', 'admin123', 'admin', 'Admin MIRU')

EXTRA_STAFF_USERS = [
    ('koordinator', 'koordinator123', 'koordinator', 'Arfan Koordinator'),
    ('petugas1', 'petugas123', 'petugas', 'Petugas Satu'),
    ('petugas2', 'petugas123', 'petugas', 'Petugas Dua'),
    ('petugas3', 'petugas123', 'petugas', 'Petugas Tiga'),
    ('pemerintah', 'pemerintah123', 'pemerintah', 'Pemerintah Distrik MIRU'),
]

# ──────────────────────────────────────────────
# Notification Templates
# ──────────────────────────────────────────────

NOTIF_KATEGORI_SAMPLES = [
    {
        'judul': 'Selamat Datang di MIRU!',
        'deskripsi': (
            'Terima kasih telah bergabung dengan MIRU Bank Sampah. '
            'Ayo mulai setorkan sampah terpilah Anda dan dapatkan saldo!'
        ),
        'kategori': 'sistem',
    },
    {
        'judul': 'Info Harga Sampah Terbaru',
        'deskripsi': (
            'Harga sampah kategori PET dan Aluminium mengalami kenaikan. '
            'Cek info harga sampah terkini di halaman utama.'
        ),
        'kategori': 'sistem',
    },
    {
        'judul': 'Jadwal Libur Nasional',
        'deskripsi': (
            'Bank sampah tutup pada tanggal 17 Agustus dalam rangka '
            'Hari Kemerdekaan RI. Silakan atur jadwal setoran Anda.'
        ),
        'kategori': 'sistem',
    },
    {
        'judul': 'Tips Pemilahan Sampah',
        'deskripsi': (
            'Pastikan sampah Anda sudah dipilah sebelum disetorkan. '
            'Sampah yang tercampur akan ditolak oleh petugas.'
        ),
        'kategori': 'sistem',
    },
    {
        'judul': 'Program Reward Bulan Ini',
        'deskripsi': (
            'Dapatkan reward spesial dengan mengumpulkan poin! '
            'Tukarkan poin Anda sekarang sebelum kehabisan.'
        ),
        'kategori': 'sistem',
    },
]


class Command(BaseCommand):
    help = (
        'Seed database with MIRU demo data. '
        'Use --minimal for core data only (categories, rewards, admin).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete existing seeded data before insert',
        )
        parser.add_argument(
            '--minimal',
            action='store_true',
            help='Seed only 8 categories, 4 rewards, and 1 admin user',
        )
        parser.add_argument(
            '--nasabah',
            type=int,
            default=180,
            help='Number of nasabah users to create in full mode (default: 180)',
        )

    def handle(self, *args, **options):
        minimal = options['minimal']

        disconnect_notification_signals()

        if options['flush']:
            self.stdout.write('Flushing data...')
            self._flush_data(minimal=minimal)

        counts = {}
        counts['categories'] = self._seed_categories()
        counts['rewards'] = self._seed_rewards()
        counts['admin'] = self._seed_admin()
        counts['settings'] = self._seed_institution_settings()
        counts['pengumuman'] = self._seed_pengumuman()

        if minimal:
            connect_notification_signals()
            total = sum(counts.values())
            self._print_summary(total, counts, minimal=True)
            return

        counts['staff'] = self._seed_extra_staff()
        nasabah_list = self._seed_nasabah(options['nasabah'])
        counts['nasabah'] = len(nasabah_list)
        counts['partners'] = self._seed_partners()
        petugas = User.objects.filter(role='petugas')

        # Separate showcase users from regular ones
        SHOWCASE_USERNAMES = {'nasabah001', 'nasabah002'}
        showcase_users = [u for u in nasabah_list if u.username in SHOWCASE_USERNAMES]
        regular_users = [u for u in nasabah_list if u.username not in SHOWCASE_USERNAMES]

        # Regular seed for all other nasabah
        counts['deposits'] = self._seed_deposits(regular_users, petugas)
        counts['pickups'] = self._seed_pickups(regular_users, petugas)
        counts['withdrawals'] = self._seed_withdrawals(regular_users)
        counts['complaints'] = self._seed_complaints(regular_users)
        counts['partner_sales'] = self._seed_partner_sales()
        counts['redemptions'] = self._seed_redemptions(regular_users)

        # Rich history for showcase users
        showcase_counts = self._seed_showcase_history(showcase_users, petugas)
        counts.update(showcase_counts)

        # Notifications for ALL users
        counts['notifications'] = self._seed_notifications(nasabah_list, showcase_users)

        connect_notification_signals()

        total = sum(counts.values())
        self._print_summary(total, counts, minimal=False)

    def _flush_data(self, minimal=False):
        if minimal:
            User.objects.filter(username=ADMIN_USER[0]).delete()
            return

        Notifikasi.objects.all().delete()
        DetailSetoran.objects.all().delete()
        TransaksiSetoran.objects.all().delete()
        Penjemputan.objects.all().delete()
        PenarikanSaldo.objects.all().delete()
        PenukaranPoin.objects.all().delete()
        Pengaduan.objects.all().delete()
        PenjualanMitra.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        KategoriSampah.objects.all().delete()
        Reward.objects.all().delete()
        MitraPengepul.objects.all().delete()

    def _print_summary(self, total, counts, minimal):
        mode = 'minimal' if minimal else 'full'

        # Calculate showcase-specific counts for display
        show_total = sum(counts.get(k, 0) for k in [
            'showcase_deposits', 'showcase_pickups', 'showcase_withdrawals',
            'showcase_complaints', 'showcase_redemptions',
        ])

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete ({mode}) — {total} records created/ensured'
        ))
        for key, value in counts.items():
            self.stdout.write(f'  {key}: {value}')
        if show_total:
            self.stdout.write(f'  showcase (nasabah001 and 002): {show_total} total transactions')
        if minimal:
            self.stdout.write(self.style.WARNING(
                '\nDemo credentials:\n'
                '  admin / admin123'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                '\nDemo credentials:\n'
                '  admin / admin123\n'
                '  koordinator / koordinator123\n'
                '  petugas1 / petugas123\n'
                '  pemerintah / pemerintah123\n'
                '  nasabah001 / nasabah123  <- Saldo & poin tertinggi!\n'
                '  nasabah002 / nasabah123  <- Saldo & poin tertinggi!'
            ))

    # ──────────────────────────────────────────────
    # Core Seed Methods
    # ──────────────────────────────────────────────

    def _seed_categories(self):
        created = 0
        for nama, harga in WASTE_CATEGORIES:
            _, was_created = KategoriSampah.objects.get_or_create(
                nama=nama,
                defaults={'harga_beli_per_kg': harga, 'stok_terkini_kg': Decimal('0.00')},
            )
            if was_created:
                created += 1
        return created or len(WASTE_CATEGORIES)

    def _seed_rewards(self):
        created = 0
        for nama, poin, stok in REWARDS:
            _, was_created = Reward.objects.get_or_create(
                nama=nama,
                defaults={'poin_dibutuhkan': poin, 'stok': stok},
            )
            if was_created:
                created += 1
        return created or len(REWARDS)

    def _seed_admin(self):
        username, password, role, nama = ADMIN_USER
        if User.objects.filter(username=username).exists():
            return 1
        User.objects.create_user(
            username=username, password=password, role=role,
            nama_lengkap=nama, no_hp='08219773690',
            alamat='Jl. Cendrawasih Poros SP.II, Timika',
        )
        return 1

    def _seed_institution_settings(self):
        PengaturanInstitusi.load()
        return 1

    def _seed_pengumuman(self):
        samples = [
            ('Selamat Datang di MIRU Bank Sampah',
             'Bank Sampah MIRU Distrik Mimika Baru siap melayani '
             'pemilahan dan setoran sampah Anda. Bawa sampah terpilah '
             'minimal 1 kg per jenis.'),
            ('Jam Operasional Libur Nasional',
             'Bank sampah tutup pada tanggal merah nasional. '
             'Silakan setor sampah di hari kerja berikutnya.'),
        ]
        created = 0
        for judul, isi in samples:
            _, was_created = Pengumuman.objects.get_or_create(
                judul=judul, defaults={'isi': isi, 'aktif': True},
            )
            if was_created:
                created += 1
        return created or len(samples)

    def _seed_extra_staff(self):
        created = 0
        for username, password, role, nama in EXTRA_STAFF_USERS:
            if User.objects.filter(username=username).exists():
                continue
            User.objects.create_user(
                username=username, password=password, role=role,
                nama_lengkap=nama,
                no_hp='0821977369{}'.format(created % 10),
                alamat='Jl. Cendrawasih Poros SP.II, Timika',
            )
            created += 1
        return created or len(EXTRA_STAFF_USERS)

    def _seed_nasabah(self, count):
        nasabah_list = []
        for i in range(1, count + 1):
            username = f'nasabah{i:03d}'

            # Showcase users get richer names and higher starting values
            if username == 'nasabah001':
                defaults = {
                    'nama_lengkap': 'Budi Santoso',
                    'role': 'nasabah',
                    'no_hp': '081234567890',
                    'alamat': 'Jl. Cendrawasih No. 42, Timika',
                    'saldo': Decimal('250000.00'),
                    'poin': 500,
                }
            elif username == 'nasabah002':
                defaults = {
                    'nama_lengkap': 'Siti Rahmawati',
                    'role': 'nasabah',
                    'no_hp': '081298765432',
                    'alamat': 'Perumahan MIRU Blok A.5, Timika',
                    'saldo': Decimal('185000.00'),
                    'poin': 350,
                }
            else:
                defaults = {
                    'nama_lengkap': f'Nasabah {i:03d}',
                    'role': 'nasabah',
                    'no_hp': f'0812{i:07d}'[:15],
                    'alamat': f'Kelurahan Timika Baru RT {i % 20:02d}',
                    'saldo': Decimal('0.00'),
                    'poin': 0,
                }

            user, created = User.objects.get_or_create(
                username=username, defaults=defaults,
            )
            if created:
                user.set_password('nasabah123')
                user.save()
            nasabah_list.append(user)
        return nasabah_list

    def _seed_partners(self):
        partners = [
            ('PT Pengepul Timika', '08123456001'),
            ('CV Sampah Jaya', '08123456002'),
            ('UD Recycling Papua', '08123456003'),
            ('Mitra Hijau Mimika', '08123456004'),
            ('Pengepul Nusantara', '08123456005'),
        ]
        created = 0
        for nama, kontak in partners:
            _, was_created = MitraPengepul.objects.get_or_create(
                nama=nama, defaults={'kontak': kontak},
            )
            if was_created:
                created += 1
        return created or len(partners)

    # ──────────────────────────────────────────────
    # Regular Seed Methods (for non-showcase users)
    # ──────────────────────────────────────────────

    def _seed_deposits(self, nasabah_list, petugas):
        categories = list(KategoriSampah.objects.all())
        if not categories or not nasabah_list:
            return 0
        petugas_user = petugas.first()
        created = 0
        for nasabah in random.sample(nasabah_list, min(60, len(nasabah_list))):
            kat = random.choice(categories)
            berat = Decimal(str(random.randint(1, 15)))
            harga = kat.harga_beli_per_kg
            subtotal = berat * harga
            transaksi = TransaksiSetoran.objects.create(
                nasabah=nasabah, petugas=petugas_user,
                total_nilai=subtotal, status='selesai',
            )
            DetailSetoran.objects.create(
                transaksi=transaksi, kategori=kat,
                berat_kg=berat, harga_saat_itu=harga, subtotal=subtotal,
            )
            nasabah.saldo += subtotal
            nasabah.poin += int(subtotal / 1000)
            nasabah.save()
            kat.stok_terkini_kg += berat
            kat.save()
            created += 1
        return created

    def _seed_pickups(self, nasabah_list, petugas):
        statuses = ['menunggu', 'disetujui', 'dijadwalkan', 'selesai', 'ditolak']
        created = 0
        for nasabah in random.sample(nasabah_list, min(40, len(nasabah_list))):
            Penjemputan.objects.create(
                nasabah=nasabah,
                petugas=random.choice(list(petugas)) if petugas else None,
                estimasi_berat=Decimal(str(random.randint(5, 30))),
                alamat_jemput=nasabah.alamat or 'Timika',
                jadwal=timezone.now() + timedelta(days=random.randint(1, 7)),
                status=random.choice(statuses),
            )
            created += 1
        return created

    def _seed_withdrawals(self, nasabah_list):
        created = 0
        candidates = [n for n in nasabah_list if n.saldo >= Decimal('50000.00')]
        for nasabah in random.sample(candidates, min(25, len(candidates))):
            PenarikanSaldo.objects.create(
                nasabah=nasabah, nominal=Decimal('50000.00'),
                metode='tunai', status=random.choice(['menunggu', 'selesai']),
            )
            created += 1
        return created

    def _seed_complaints(self, nasabah_list):
        keluhan_samples = [
            ('Saldo belum masuk setelah setoran.', 'saldo_belum_masuk'),
            ('Jadwal penjemputan terlambat.', 'penjemputan_terlambat'),
            ('Berat sampah tidak sesuai timbangan.', 'berat_tidak_sesuai'),
            ('Petugas belum datang sesuai jadwal.', 'petugas_tidak_datang'),
        ]
        created = 0
        for nasabah in random.sample(nasabah_list, min(20, len(nasabah_list))):
            keluhan, jenis = random.choice(keluhan_samples)
            Pengaduan.objects.create(
                nasabah=nasabah, jenis_pengaduan=jenis,
                keluhan=keluhan, status=random.choice(['terbuka', 'ditutup']),
            )
            created += 1
        return created

    def _seed_partner_sales(self):
        partners = list(MitraPengepul.objects.all())
        categories = list(KategoriSampah.objects.all())
        if not partners or not categories:
            return 0
        created = 0
        for _ in range(10):
            kat = random.choice(categories)
            berat = Decimal(str(random.randint(10, 50)))
            harga = Decimal(str(random.randint(2000, 8000)))
            PenjualanMitra.objects.create(
                mitra=random.choice(partners), kategori=kat,
                berat_jual_kg=berat, harga_jual_per_kg=harga,
                total_penjualan=berat * harga,
            )
            created += 1
        return created

    def _seed_redemptions(self, nasabah_list):
        rewards = list(Reward.objects.all())
        candidates = [n for n in nasabah_list if n.poin >= 50]
        if not rewards or not candidates:
            return 0
        created = 0
        for nasabah in random.sample(candidates, min(15, len(candidates))):
            reward = random.choice(rewards)
            if nasabah.poin >= reward.poin_dibutuhkan:
                PenukaranPoin.objects.create(
                    nasabah=nasabah, reward=reward,
                    status=random.choice(['menunggu', 'selesai']),
                )
                created += 1
        return created

    # ──────────────────────────────────────────────
    # Showcase History — nasabah001 & nasabah002
    # ──────────────────────────────────────────────

    def _seed_showcase_history(self, showcase_users, petugas):
        """
        Create rich history for nasabah001 (Budi Santoso) and
        nasabah002 (Siti Rahmawati) — the two users with
        highest saldo, poin, and most transaction variety.
        """
        counts = {
            'showcase_deposits': 0,
            'showcase_pickups': 0,
            'showcase_withdrawals': 0,
            'showcase_complaints': 0,
            'showcase_redemptions': 0,
        }

        if not showcase_users:
            return counts

        categories = list(KategoriSampah.objects.all())
        if not categories:
            return counts

        petugas_user = petugas.first() if petugas else None
        now = timezone.now()

        # Helper to create a timed deposit
        def _make_deposit(user, days_ago, kategori, berat_kg, petugas=None):
            harga = kategori.harga_beli_per_kg
            subtotal = berat_kg * harga
            tanggal = now - timedelta(days=days_ago, hours=random.randint(0, 23))
            transaksi = TransaksiSetoran.objects.create(
                nasabah=user, petugas=petugas,
                total_nilai=subtotal, status='selesai',
            )
            # Override auto_now_add date
            TransaksiSetoran.objects.filter(pk=transaksi.pk).update(tanggal=tanggal)
            DetailSetoran.objects.create(
                transaksi=transaksi, kategori=kategori,
                berat_kg=berat_kg, harga_saat_itu=harga, subtotal=subtotal,
            )
            # Update user balance
            user.saldo += subtotal
            user.poin += int(subtotal / 1000)
            user.save()
            counts['showcase_deposits'] += 1

        # Helper to create a timed pickup
        def _make_pickup(user, days_ago, status, berat, petugas=None):
            jadwal = now - timedelta(days=days_ago - 1)
            Penjemputan.objects.create(
                nasabah=user, petugas=petugas,
                estimasi_berat=berat,
                alamat_jemput=user.alamat or 'Timika',
                jadwal=jadwal, status=status,
            )
            counts['showcase_pickups'] += 1

        # ════════════════════════════════════════
        # nasabah001 — Budi Santoso
        # ════════════════════════════════════════
        budi = None
        siti = None
        for u in showcase_users:
            if u.username == 'nasabah001':
                budi = u
            elif u.username == 'nasabah002':
                siti = u

        if budi:
            # Budi: 18 deposits across 3 months — highest volume
            deposits_budi = [
                # (days_ago, kategori_index, berat_kg)
                (90, 0, 5),   # PET 5kg
                (85, 3, 3),   # Kertas 3kg
                (80, 4, 2),   # Aluminium 2kg (high value)
                (72, 2, 8),   # Kardus 8kg
                (65, 6, 10),  # Kaca 10kg
                (58, 0, 7),   # PET 7kg
                (52, 4, 3),   # Aluminium 3kg
                (46, 1, 6),   # Gelas Plastik 6kg
                (40, 7, 4),   # Jelantah 4kg (high value)
                (34, 2, 12),  # Kardus 12kg
                (28, 5, 5),   # Besi 5kg
                (23, 0, 8),   # PET 8kg
                (19, 4, 4),   # Aluminium 4kg
                (15, 1, 7),   # Gelas Plastik 7kg
                (11, 7, 5),   # Jelantah 5kg
                (7,  2, 10),  # Kardus 10kg
                (4,  0, 6),   # PET 6kg
                (1,  3, 5),   # Kertas 5kg
            ]
            for days_ago, kat_idx, berat in deposits_budi:
                _make_deposit(budi, days_ago, categories[kat_idx],
                               Decimal(str(berat)), petugas_user)

            # Budi: 6 pickups — mix of statuses
            pickups_budi = [
                (80, 'selesai', Decimal('10.00')),
                (55, 'selesai', Decimal('25.00')),
                (30, 'selesai', Decimal('15.00')),
                (15, 'dijadwalkan', Decimal('20.00')),
                (7,  'disetujui', Decimal('30.00')),
                (2,  'menunggu', Decimal('12.00')),
            ]
            for days_ago, status, berat in pickups_budi:
                _make_pickup(budi, days_ago, status, berat, petugas_user)

            # Budi: 4 withdrawals — 2 selesai, 1 ditolak, 1 menunggu
            PenarikanSaldo.objects.create(
                nasabah=budi, nominal=Decimal('50000.00'),
                metode='tunai', status='selesai',
            )
            PenarikanSaldo.objects.create(
                nasabah=budi, nominal=Decimal('100000.00'),
                metode='tunai', status='selesai',
            )
            PenarikanSaldo.objects.create(
                nasabah=budi, nominal=Decimal('75000.00'),
                metode='tunai', status='ditolak',
            )
            PenarikanSaldo.objects.create(
                nasabah=budi, nominal=Decimal('50000.00'),
                metode='tunai', status='menunggu',
            )
            counts['showcase_withdrawals'] += 4

            # Budi: 2 redemptions — 1 selesai, 1 menunggu
            rewards = list(Reward.objects.all())
            if rewards:
                PenukaranPoin.objects.create(
                    nasabah=budi, reward=rewards[0], status='selesai',
                )
                if len(rewards) > 1:
                    PenukaranPoin.objects.create(
                        nasabah=budi, reward=rewards[1], status='menunggu',
                    )
                counts['showcase_redemptions'] += 2

            # Budi: 2 complaints — 1 closed, 1 open
            Pengaduan.objects.create(
                nasabah=budi, jenis_pengaduan='berat_tidak_sesuai',
                keluhan='Berat sampah kardus saya 15kg tapi dicatat 10kg.',
                tindak_lanjut='Mohon maaf, sudah dikoreksi oleh admin. '
                              'Selisih 5kg sudah ditambahkan ke saldo.',
                status='ditutup',
            )
            Pengaduan.objects.create(
                nasabah=budi, jenis_pengaduan='saldo_belum_masuk',
                keluhan='Setoran tanggal 3 Juli 2026 belum masuk ke saldo '
                        'sampai sekarang. Mohon segera diproses.',
                status='terbuka',
            )
            counts['showcase_complaints'] += 2

        # ════════════════════════════════════════
        # nasabah002 — Siti Rahmawati
        # ════════════════════════════════════════
        if siti:
            # Siti: 15 deposits — slightly less than Budi
            deposits_siti = [
                (88, 0, 4),   # PET 4kg
                (82, 1, 5),   # Gelas Plastik 5kg
                (75, 2, 6),   # Kardus 6kg
                (68, 4, 2),   # Aluminium 2kg
                (60, 7, 3),   # Jelantah 3kg
                (54, 0, 6),   # PET 6kg
                (48, 3, 4),   # Kertas 4kg
                (42, 5, 3),   # Besi 3kg
                (36, 1, 8),   # Gelas Plastik 8kg
                (30, 6, 15),  # Kaca 15kg
                (24, 4, 3),   # Aluminium 3kg
                (18, 0, 5),   # PET 5kg
                (12, 7, 4),   # Jelantah 4kg
                (6,  2, 8),   # Kardus 8kg
                (2,  3, 3),   # Kertas 3kg
            ]
            for days_ago, kat_idx, berat in deposits_siti:
                _make_deposit(siti, days_ago, categories[kat_idx],
                               Decimal(str(berat)), petugas_user)

            # Siti: 4 pickups
            pickups_siti = [
                (70, 'selesai', Decimal('8.00')),
                (45, 'selesai', Decimal('12.00')),
                (20, 'selesai', Decimal('15.00')),
                (5,  'dalam_perjalanan', Decimal('10.00')),
            ]
            for days_ago, status, berat in pickups_siti:
                _make_pickup(siti, days_ago, status, berat, petugas_user)

            # Siti: 3 withdrawals — 1 selesai, 2 menunggu
            PenarikanSaldo.objects.create(
                nasabah=siti, nominal=Decimal('50000.00'),
                metode='tunai', status='selesai',
            )
            PenarikanSaldo.objects.create(
                nasabah=siti, nominal=Decimal('50000.00'),
                metode='tunai', status='menunggu',
            )
            PenarikanSaldo.objects.create(
                nasabah=siti, nominal=Decimal('100000.00'),
                metode='tunai', status='menunggu',
            )
            counts['showcase_withdrawals'] += 3

            # Siti: 2 redemptions — 1 selesai, 1 menunggu
            rewards = list(Reward.objects.all())
            if rewards:
                PenukaranPoin.objects.create(
                    nasabah=siti, reward=rewards[0], status='selesai',
                )
                if len(rewards) > 1:
                    PenukaranPoin.objects.create(
                        nasabah=siti, reward=rewards[2], status='menunggu',
                    )
                counts['showcase_redemptions'] += 2

            # Siti: 1 complaint — open
            Pengaduan.objects.create(
                nasabah=siti, jenis_pengaduan='penjemputan_terlambat',
                keluhan='Penjemputan dijadwalkan jam 09.00 tapi petugas '
                        'datang jam 14.00. Saya sudah menunggu lama.',
                status='terbuka',
            )
            counts['showcase_complaints'] += 1

        return counts

    # ──────────────────────────────────────────────
    # Notification Seed
    # ──────────────────────────────────────────────

    def _seed_notifications(self, nasabah_list, showcase_users=None):
        if not nasabah_list:
            return 0

        created = 0
        now = timezone.now()
        total = len(nasabah_list)

        # Always include showcase users in primary group
        showcase_usernames = {u.username for u in (showcase_users or [])}
        other_users = [u for u in nasabah_list if u.username not in showcase_usernames]

        primary_count = min(10, total)
        primary_pool = list(showcase_users or []) + other_users
        primary_users = random.sample(primary_pool, min(primary_count, len(primary_pool)))

        # ── Sistem notifications ──
        for user in primary_users:
            for sample in NOTIF_KATEGORI_SAMPLES:
                Notifikasi.objects.create(
                    user=user, judul=sample['judul'],
                    deskripsi=sample['deskripsi'], kategori=sample['kategori'],
                    is_read=random.random() < 0.4,
                    created_at=now - timedelta(hours=random.randint(1, 72)),
                )
                created += 1

        # ── Setoran notifications ──
        setoran_count = min(40, total)
        for user in random.sample(nasabah_list, setoran_count):
            nilai = Decimal(str(random.randint(10000, 200000)))
            Notifikasi.objects.create(
                user=user, judul='Setoran Sampah Berhasil',
                deskripsi=f'Setoran sampah sebesar Rp{nilai:,.0f} telah dicatat ke akun Anda. Cek saldo di halaman utama.',
                kategori='setoran', is_read=random.random() < 0.6,
                created_at=now - timedelta(hours=random.randint(1, 48)),
            )
            created += 1

        # ── Penjemputan notifications ──
        pickup_statuses = [
            ('Penjemputan Disetujui', 'Penjemputan sampah Anda telah disetujui. Petugas akan segera dijadwalkan.'),
            ('Penjemputan Dijadwalkan', 'Penjemputan sampah Anda telah dijadwalkan. Mohon siapkan sampah Anda.'),
            ('Petugas Dalam Perjalanan', 'Petugas MIRU sedang dalam perjalanan ke lokasi Anda.'),
            ('Penjemputan Selesai', 'Penjemputan sampah Anda telah selesai. Saldo akan bertambah setelah setoran dicatat.'),
            ('Penjemputan Ditolak', 'Mohon maaf, penjemputan sampah Anda ditolak. Hubungi admin MIRU.'),
        ]
        pickup_count = min(30, total)
        for user in random.sample(nasabah_list, pickup_count):
            judul, deskripsi = random.choice(pickup_statuses)
            Notifikasi.objects.create(
                user=user, judul=judul, deskripsi=deskripsi,
                kategori='penjemputan', is_read=random.random() < 0.5,
                created_at=now - timedelta(hours=random.randint(2, 72)),
            )
            created += 1

        # ── Penarikan notifications ──
        penarikan_statuses = [
            ('Penarikan Saldo Diajukan', 'Pengajuan penarikan saldo telah diterima. Tunggu proses persetujuan admin (1-2 hari kerja).'),
            ('Penarikan Saldo Disetujui', 'Penarikan saldo telah disetujui. Saldo Anda telah terpotong. Silakan ambil tunai di kantor MIRU.'),
            ('Penarikan Saldo Ditolak', 'Mohon maaf, penarikan saldo ditolak. Hubungi admin MIRU untuk informasi lebih lanjut.'),
        ]
        penarikan_count = min(20, total)
        for user in random.sample(nasabah_list, penarikan_count):
            judul, deskripsi = random.choice(penarikan_statuses)
            Notifikasi.objects.create(
                user=user, judul=judul, deskripsi=deskripsi,
                kategori='penarikan', is_read=random.random() < 0.3,
                created_at=now - timedelta(hours=random.randint(4, 96)),
            )
            created += 1

        # ── Penukaran notifications ──
        rewards_names = ['Pulsa', 'Bibit', 'Sembako', 'Alat Kebersihan']
        penukaran_count = min(15, total)
        for user in random.sample(nasabah_list, penukaran_count):
            reward = random.choice(rewards_names)
            if random.random() < 0.7:
                Notifikasi.objects.create(
                    user=user, judul='Penukaran Poin Berhasil',
                    deskripsi=f'Selamat! Penukaran poin untuk {reward} telah disetujui. Hubungi admin MIRU untuk pengambilan reward.',
                    kategori='penukaran', is_read=random.random() < 0.4,
                    created_at=now - timedelta(hours=random.randint(6, 72)),
                )
            else:
                Notifikasi.objects.create(
                    user=user, judul='Penukaran Poin Diajukan',
                    deskripsi=f'Penukaran poin untuk {reward} telah diajukan. Tunggu persetujuan admin.',
                    kategori='penukaran', is_read=False,
                    created_at=now - timedelta(hours=random.randint(1, 12)),
                )
            created += 1

        # ── Pengaduan notifications ──
        pengaduan_count = min(15, total)
        for user in random.sample(nasabah_list, pengaduan_count):
            if random.random() < 0.5:
                Notifikasi.objects.create(
                    user=user, judul='Pengaduan Diterima',
                    deskripsi='Pengaduan Anda telah diterima. Admin akan menindaklanjuti maksimal 2 hari kerja.',
                    kategori='pengaduan', is_read=random.random() < 0.3,
                    created_at=now - timedelta(hours=random.randint(1, 24)),
                )
            else:
                Notifikasi.objects.create(
                    user=user, judul='Pengaduan Telah Ditindaklanjuti',
                    deskripsi='Pengaduan Anda telah ditindaklanjuti oleh admin. Lihat detail di menu Pengaduan.',
                    kategori='pengaduan', is_read=random.random() < 0.5,
                    created_at=now - timedelta(hours=random.randint(6, 48)),
                )
            created += 1

        distinct_users = Notifikasi.objects.values('user').distinct().count()
        self.stdout.write(
            f'  Seeded {created} notifications across {distinct_users} users'
        )
        return created
