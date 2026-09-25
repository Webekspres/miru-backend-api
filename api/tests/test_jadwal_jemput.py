from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from api.models import JadwalJemputWilayah, Notifikasi, Penjemputan, WilayahLayanan
from api.services.jadwal_jemput import format_tanggal_id
from api.services.pickups import week_bounds_wit

from .base import EnvelopeAPITestCase

WIT = ZoneInfo('Asia/Jayapura')


class HelperTests(TestCase):
    def test_week_is_monday_to_monday_in_wit(self):
        ref = datetime(2026, 9, 27, 23, 30, tzinfo=WIT)
        start, end = week_bounds_wit(ref)
        self.assertEqual(start, datetime(2026, 9, 21, tzinfo=WIT))
        self.assertEqual(end, datetime(2026, 9, 28, tzinfo=WIT))

    def test_format_tanggal_id(self):
        self.assertEqual(format_tanggal_id(datetime(2026, 9, 29).date()), 'Selasa, 29 September 2026')


class JadwalJemputApiTests(EnvelopeAPITestCase):
    def setUp(self):
        self.wilayah = WilayahLayanan.objects.create(kelurahan='Kwamki')
        self.other = WilayahLayanan.objects.create(kelurahan='Nawaripi')
        self.admin = self.create_admin(username='admin_jadwal')
        self.warga = self._warga('warga_kwamki', self.wilayah)
        self.warga_lain = self._warga('warga_nawaripi', self.other)
        today = timezone.now().astimezone(WIT).date()
        # Senin minggu depan — seluruh minggunya pasti di masa depan.
        self.monday = today + timedelta(days=7 - today.weekday())

    def _warga(self, username, wilayah):
        user = self.create_nasabah(username=username)
        user.kelurahan = wilayah
        user.save()
        return user

    def _create(self, tanggal, wilayah=None, **extra):
        self.auth_as(self.admin)
        return self.client.post('/api/jadwal-jemput/', {
            'wilayah': (wilayah or self.wilayah).id,
            'tanggal': tanggal.isoformat(),
            'jam_mulai': '08:00',
            'jam_selesai': '12:00',
            **extra,
        }, format='json')

    def test_admin_creates_and_wilayah_nasabah_notified(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self._create(self.monday + timedelta(days=1))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['jumlah_pesanan'], 0)
        self.assertTrue(response.data['data']['bisa_dipesan'])

        notif = Notifikasi.objects.get(user=self.warga, kategori='jadwal_jemput')
        self.assertIn('Kwamki', notif.deskripsi)
        self.assertIn('Selasa', notif.deskripsi)
        self.assertIn('08.00–12.00 WIT', notif.deskripsi)
        self.assertIn('Segera jadwalkan penjemputan Anda', notif.deskripsi)
        self.assertFalse(Notifikasi.objects.filter(user=self.warga_lain, kategori='jadwal_jemput').exists())

    def test_max_two_per_week_any_days(self):
        self.assertEqual(self._create(self.monday).status_code, 201)
        self.assertEqual(self._create(self.monday + timedelta(days=4)).status_code, 201)
        third = self._create(self.monday + timedelta(days=6))
        self.assertEqual(third.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Maksimal 2', third.data['message'])
        # Minggu berikutnya dan wilayah lain tidak terpengaruh.
        self.assertEqual(self._create(self.monday + timedelta(days=7)).status_code, 201)
        self.assertEqual(self._create(self.monday + timedelta(days=6), wilayah=self.other).status_code, 201)

    def test_same_date_twice_rejected(self):
        self._create(self.monday)
        response = self._create(self.monday)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_today_rejected(self):
        response = self._create(timezone.now().astimezone(WIT).date())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_jam_selesai_before_mulai_rejected(self):
        response = self._create(self.monday, jam_mulai='12:00', jam_selesai='08:00')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nasabah_cannot_create(self):
        self.auth_as(self.warga)
        response = self.client.post('/api/jadwal-jemput/', {
            'wilayah': self.wilayah.id, 'tanggal': self.monday.isoformat(),
            'jam_mulai': '08:00', 'jam_selesai': '12:00',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nasabah_lists_only_own_bookable_jadwal(self):
        mine = JadwalJemputWilayah.objects.create(
            wilayah=self.wilayah, tanggal=self.monday, jam_mulai=time(8), jam_selesai=time(12),
        )
        JadwalJemputWilayah.objects.create(
            wilayah=self.wilayah, tanggal=timezone.now().astimezone(WIT).date(),
            jam_mulai=time(8), jam_selesai=time(12),
        )
        JadwalJemputWilayah.objects.create(
            wilayah=self.other, tanggal=self.monday, jam_mulai=time(8), jam_selesai=time(12),
        )
        self.auth_as(self.warga)
        response = self.client.get('/api/jadwal-jemput/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([j['id'] for j in response.data['data']], [mine.id])

    def test_admin_filters_by_week(self):
        this_week = self._create(self.monday).data['data']['id']
        self._create(self.monday + timedelta(days=7))
        self.auth_as(self.admin)
        response = self.client.get(
            f'/api/jadwal-jemput/?tanggal={(self.monday + timedelta(days=3)).isoformat()}',
        )
        self.assertEqual([j['id'] for j in response.data['data']], [this_week])

    def test_delete_blocked_when_booked(self):
        jadwal_id = self._create(self.monday).data['data']['id']
        jadwal = JadwalJemputWilayah.objects.get(pk=jadwal_id)
        Penjemputan.objects.create(
            nasabah=self.warga, estimasi_berat='6', alamat_jemput='Jl. A',
            jadwal=timezone.now() + timedelta(days=7), jadwal_wilayah=jadwal,
        )
        self.auth_as(self.admin)
        response = self.client.delete(f'/api/jadwal-jemput/{jadwal_id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.get('/api/jadwal-jemput/').data['data'][0]['jumlah_pesanan'], 1)

    def test_delete_without_bookings(self):
        jadwal_id = self._create(self.monday).data['data']['id']
        response = self.client.delete(f'/api/jadwal-jemput/{jadwal_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(JadwalJemputWilayah.objects.filter(pk=jadwal_id).exists())
