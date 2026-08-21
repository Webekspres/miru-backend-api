from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from api.models import KontenEdukasi, KategoriSampah, Reward

User = get_user_model()

EXPECTED_CATEGORIES = [
    'PET', 'Gelas Plastik', 'Kardus', 'Kertas',
    'Aluminium', 'Besi', 'Kaca', 'Jelantah',
]

EXPECTED_REWARDS = [
    'Pulsa', 'Bibit', 'Sembako', 'Alat Kebersihan',
]


class SeedDataMinimalTests(TestCase):
    def test_minimal_seed_creates_core_data(self):
        out = StringIO()
        call_command('seed_data', '--minimal', '--flush', stdout=out)

        self.assertEqual(KategoriSampah.objects.count(), 8)
        self.assertEqual(
            set(KategoriSampah.objects.values_list('nama', flat=True)),
            set(EXPECTED_CATEGORIES),
        )

        self.assertEqual(Reward.objects.count(), 4)
        self.assertEqual(
            set(Reward.objects.values_list('nama', flat=True)),
            set(EXPECTED_REWARDS),
        )

        admin = User.objects.get(username='admin')
        self.assertEqual(admin.role, 'admin')
        self.assertTrue(admin.check_password('admin123'))
        self.assertTrue(admin.avatar_url.startswith('avatar/'))
        self.assertTrue(admin.avatar_url.endswith('.webp'))

        articles = KontenEdukasi.objects.all()
        self.assertEqual(articles.count(), 7)
        for article in articles:
            self.assertTrue(article.gambar_url.startswith('edukasi/'))
            self.assertTrue(article.gambar_url.endswith('.webp'))

    def test_minimal_seed_is_idempotent(self):
        call_command('seed_data', '--minimal', '--flush', stdout=StringIO())
        call_command('seed_data', '--minimal', stdout=StringIO())

        self.assertEqual(KategoriSampah.objects.count(), 8)
        self.assertEqual(Reward.objects.count(), 4)
        self.assertEqual(User.objects.filter(role='admin').count(), 1)


class SeedDataFullTests(TestCase):
    def test_full_seed_creates_200_plus_records(self):
        call_command('seed_data', '--flush', '--nasabah', '180', stdout=StringIO())

        total = (
            KategoriSampah.objects.count()
            + Reward.objects.count()
            + User.objects.count()
        )
        self.assertGreaterEqual(User.objects.count(), 180)
        self.assertTrue(User.objects.filter(username='nasabah001').exists())
        self.assertTrue(User.objects.filter(username='koordinator').exists())
        budi = User.objects.get(username='nasabah001')
        self.assertTrue(budi.avatar_url.startswith('avatar/'))
        self.assertTrue(
            KontenEdukasi.objects.exclude(gambar_url='').count() >= 7,
        )
