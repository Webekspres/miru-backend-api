import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import (
    DetailSetoran,
    KategoriSampah,
    MitraPengepul,
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
            total = sum(counts.values())
            self._print_summary(total, counts, minimal=True)
            return

        counts['staff'] = self._seed_extra_staff()
        nasabah_list = self._seed_nasabah(options['nasabah'])
        counts['nasabah'] = len(nasabah_list)
        counts['partners'] = self._seed_partners()
        petugas = User.objects.filter(role='petugas')
        counts['deposits'] = self._seed_deposits(nasabah_list, petugas)
        counts['pickups'] = self._seed_pickups(nasabah_list, petugas)
        counts['withdrawals'] = self._seed_withdrawals(nasabah_list)
        counts['complaints'] = self._seed_complaints(nasabah_list)
        counts['partner_sales'] = self._seed_partner_sales()
        counts['redemptions'] = self._seed_redemptions(nasabah_list)

        total = sum(counts.values())
        self._print_summary(total, counts, minimal=False)

    def _flush_data(self, minimal=False):
        if minimal:
            User.objects.filter(username=ADMIN_USER[0]).delete()
            return

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
        self.stdout.write(self.style.SUCCESS(
            f'Seed complete ({mode}) — {total} records created/ensured'
        ))
        for key, value in counts.items():
            self.stdout.write(f'  {key}: {value}')
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
                '  nasabah001 / nasabah123'
            ))

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
            username=username,
            password=password,
            role=role,
            nama_lengkap=nama,
            no_hp='08219773690',
            alamat='Jl. Cendrawasih Poros SP.II, Timika',
        )
        return 1

    def _seed_institution_settings(self):
        PengaturanInstitusi.load()
        return 1

    def _seed_pengumuman(self):
        samples = [
            (
                'Selamat Datang di MIRU Bank Sampah',
                'Bank Sampah MIRU Distrik Mimika Baru siap melayani '
                'pemilahan dan setoran sampah Anda. Bawa sampah terpilah '
                'minimal 1 kg per jenis.',
            ),
            (
                'Jam Operasional Libur Nasional',
                'Bank sampah tutup pada tanggal merah nasional. '
                'Silakan setor sampah di hari kerja berikutnya.',
            ),
        ]
        created = 0
        for judul, isi in samples:
            _, was_created = Pengumuman.objects.get_or_create(
                judul=judul,
                defaults={'isi': isi, 'aktif': True},
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
                username=username,
                password=password,
                role=role,
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
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'nama_lengkap': f'Nasabah {i:03d}',
                    'role': 'nasabah',
                    'no_hp': f'0812{i:07d}'[:15],
                    'alamat': f'Kelurahan Timika Baru RT {i % 20:02d}',
                    'saldo': Decimal('0.00'),
                    'poin': 0,
                },
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
                nasabah=nasabah,
                petugas=petugas_user,
                total_nilai=subtotal,
                status='selesai',
            )
            DetailSetoran.objects.create(
                transaksi=transaksi,
                kategori=kat,
                berat_kg=berat,
                harga_saat_itu=harga,
                subtotal=subtotal,
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
            nominal = Decimal('50000.00')
            PenarikanSaldo.objects.create(
                nasabah=nasabah,
                nominal=nominal,
                metode='tunai',
                status=random.choice(['menunggu', 'selesai']),
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
                nasabah=nasabah,
                jenis_pengaduan=jenis,
                keluhan=keluhan,
                status=random.choice(['terbuka', 'ditutup']),
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
                mitra=random.choice(partners),
                kategori=kat,
                berat_jual_kg=berat,
                harga_jual_per_kg=harga,
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
                    nasabah=nasabah,
                    reward=reward,
                    status=random.choice(['menunggu', 'selesai']),
                )
                created += 1
        return created
