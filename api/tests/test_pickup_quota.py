from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.utils import timezone
from rest_framework import status

from api.models import Penjemputan, WilayahLayanan
from api.services.pickups import week_bounds_wit

from .base import EnvelopeAPITestCase

WIT = ZoneInfo('Asia/Jayapura')


class WeekBoundsTests(EnvelopeAPITestCase):
    def test_week_is_monday_to_monday_in_wit(self):
        # Minggu 2026-09-27 23:30 WIT = Minggu 14:30 UTC → tetap minggu 21–27 Sep.
        ref = datetime(2026, 9, 27, 23, 30, tzinfo=WIT)
        start, end = week_bounds_wit(ref)
        self.assertEqual(start, datetime(2026, 9, 21, tzinfo=WIT))
        self.assertEqual(end, datetime(2026, 9, 28, tzinfo=WIT))


class PickupQuotaTests(EnvelopeAPITestCase):
    def setUp(self):
        self.wilayah = WilayahLayanan.objects.create(kelurahan='Kwamki')
        self.nasabah = self._warga('warga_a')
        self.admin = self.create_admin(username='admin_kuota')
        now = timezone.now().astimezone(WIT)
        # Rabu minggu depan & Rabu dua minggu lagi — selalu > 1 jam ke depan.
        next_monday = (now + timedelta(days=7 - now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        self.week1 = next_monday + timedelta(days=2, hours=9)
        self.week2 = self.week1 + timedelta(days=7)

    def _warga(self, username):
        user = self.create_nasabah(username=username)
        user.kelurahan = self.wilayah
        user.save()
        return user

    def _existing(self, jadwal, status_='menunggu'):
        return Penjemputan.objects.create(
            nasabah=self._warga(f'warga_{Penjemputan.objects.count()}_{status_}'),
            estimasi_berat='6.00', alamat_jemput='Jl. A', jadwal=jadwal,
            status=status_,
        )

    def _submit(self, jadwal):
        self.auth_as(self.nasabah)
        return self.client.post('/api/pickups/', {
            'estimasi_berat': '6.00',
            'alamat_jemput': 'Jl. Cendrawasih',
            'jadwal': jadwal.isoformat(),
        }, format='json')

    def test_full_week_rejected_with_message(self):
        self._existing(self.week1)
        self._existing(self.week1 + timedelta(days=1))
        response = self._submit(self.week1 + timedelta(hours=2))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('jadwal', response.data['errors'])
        self.assertIn('Maksimal 2x', response.data['message'])

    def test_pickups_in_other_week_do_not_use_quota(self):
        # Dua jemput di minggu berikutnya tidak boleh memblokir minggu ini.
        self._existing(self.week2)
        self._existing(self.week2 + timedelta(days=1))
        response = self._submit(self.week1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_rejected_and_cancelled_do_not_count(self):
        self._existing(self.week1, status_='ditolak')
        self._existing(self.week1, status_='dibatalkan')
        self._existing(self.week1)
        response = self._submit(self.week1 + timedelta(hours=2))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_kuota_endpoint(self):
        self._existing(self.week1)
        self.auth_as(self.admin)
        response = self.client.get(
            f'/api/wilayah/kuota/?tanggal={self.week1.date().isoformat()}',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        row = next(r for r in response.data['data'] if r['id'] == self.wilayah.id)
        self.assertEqual((row['terpakai'], row['maks'], row['sisa']), (1, 2, 1))
        self.assertEqual(response.data['meta']['minggu_mulai'], (self.week1 - timedelta(days=2)).date().isoformat())

    def test_kuota_endpoint_bad_date(self):
        self.auth_as(self.admin)
        response = self.client.get('/api/wilayah/kuota/?tanggal=kemarin')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_kuota_endpoint_forbidden_for_nasabah(self):
        self.auth_as(self.nasabah)
        response = self.client.get('/api/wilayah/kuota/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
