from datetime import time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.utils import timezone
from rest_framework import status

from api.models import Notifikasi, Penjemputan, PengaturanInstitusi

from .base import EnvelopeAPITestCase

WIT = ZoneInfo('Asia/Jayapura')


class PickupCreateTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah(username='nasabah_pickup')
        self.petugas = self.create_petugas()
        self.admin = self.create_admin(username='admin_pickup')
        self.jadwal = (timezone.now().astimezone(WIT) + timedelta(days=2)).replace(
            hour=9, minute=0, second=0, microsecond=0,
        )

    def _payload(self, **overrides):
        payload = {
            'estimasi_berat': '8.00',
            'alamat_jemput': 'Jl. Cendrawasih, Timika',
            'jadwal': self.jadwal.isoformat(),
        }
        payload.update(overrides)
        return payload

    def test_nasabah_create_success(self):
        self.auth_as(self.nasabah)
        response = self.client.post('/api/pickups/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data['data']
        self.assertEqual(data['status'], 'menunggu')
        self.assertEqual(data['nasabah'], self.nasabah.id)
        self.assertIsNone(data['petugas'])

    def test_create_out_of_hours_sets_meta_warning(self):
        settings = PengaturanInstitusi.load()
        settings.jam_buka = time(8, 0)
        settings.jam_tutup = time(17, 0)
        settings.save()

        late = (timezone.now().astimezone(WIT) + timedelta(days=2)).replace(
            hour=20, minute=0, second=0, microsecond=0,
        )
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/pickups/',
            self._payload(jadwal=late.isoformat()),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['meta'].get('di_luar_jam_layanan'))
        self.assertIn('peringatan', response.data['meta'])

    def test_create_within_hours_no_out_of_hours_meta(self):
        settings = PengaturanInstitusi.load()
        settings.jam_buka = time(8, 0)
        settings.jam_tutup = time(17, 0)
        settings.save()

        self.auth_as(self.nasabah)
        response = self.client.post('/api/pickups/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['meta'].get('di_luar_jam_layanan', False))

    def test_create_with_optional_coordinates(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/pickups/',
            self._payload(
                latitude='-4.543210',
                longitude='136.540123',
                catatan_lokasi='Dekat warung Bu Siti',
            ),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data['data']
        self.assertEqual(data['latitude'], '-4.543210')
        self.assertEqual(data['longitude'], '136.540123')
        self.assertEqual(data['catatan_lokasi'], 'Dekat warung Bu Siti')

    def test_reject_invalid_latitude(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/pickups/',
            self._payload(latitude='99.0', longitude='136.5'),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_weight_below_5kg(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/pickups/',
            self._payload(estimasi_berat='4.00'),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_jadwal_in_past(self):
        self.auth_as(self.nasabah)
        past = timezone.now() - timedelta(hours=2)
        response = self.client.post(
            '/api/pickups/',
            self._payload(jadwal=past.isoformat()),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_jadwal_less_than_one_hour(self):
        self.auth_as(self.nasabah)
        soon = timezone.now() + timedelta(minutes=30)
        response = self.client.post(
            '/api/pickups/',
            self._payload(jadwal=soon.isoformat()),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_jadwal_more_than_one_hour(self):
        self.auth_as(self.nasabah)
        ahead = timezone.now() + timedelta(hours=2)
        response = self.client.post(
            '/api/pickups/',
            self._payload(jadwal=ahead.isoformat()),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_notifies_admin_and_koordinator(self):
        admin = self.admin
        koord = self.create_koordinator(username='koord_pickup_notif')
        self.auth_as(self.nasabah)
        response = self.client.post('/api/pickups/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pickup_id = response.data['data']['id']

        admin_notif = Notifikasi.objects.filter(
            user=admin, kategori='penjemputan', judul='Penjemputan Baru',
        ).first()
        self.assertIsNotNone(admin_notif)
        self.assertIn(str(pickup_id), admin_notif.deskripsi)
        self.assertIn('segera tindak lanjuti', admin_notif.deskripsi.lower())

        koord_notif = Notifikasi.objects.filter(
            user=koord, kategori='penjemputan', judul='Penjemputan Baru',
        ).first()
        self.assertIsNotNone(koord_notif)

    def test_petugas_cannot_create(self):
        self.auth_as(self.petugas)
        response = self.client.post('/api/pickups/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nasabah_cannot_set_other_nasabah(self):
        other = self.create_nasabah(username='nasabah_other')
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/pickups/',
            {**self._payload(), 'nasabah': other.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['nasabah'], self.nasabah.id)


class PickupWorkflowTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah(username='nasabah_flow')
        self.petugas = self.create_petugas()
        self.other_petugas = self.create_petugas(username='petugas_other')
        self.admin = self.create_admin(username='admin_flow')
        self.pickup = Penjemputan.objects.create(
            nasabah=self.nasabah,
            estimasi_berat=Decimal('10.00'),
            alamat_jemput='Timika',
            jadwal=timezone.now() + timedelta(days=3),
            status='menunggu',
        )

    def test_admin_approve_requires_petugas(self):
        """Tidak boleh disetujui tanpa petugas."""
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'disetujui'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_approve_and_assign_atomic_via_patch(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'disetujui', 'petugas': self.petugas.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'dijadwalkan')
        self.assertEqual(response.data['data']['petugas'], self.petugas.id)

    def test_admin_schedule_from_menunggu_with_petugas(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'dijadwalkan', 'petugas': self.petugas.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'dijadwalkan')
        self.assertEqual(response.data['data']['petugas'], self.petugas.id)

    def test_admin_reject(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'ditolak'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'ditolak')

    def test_petugas_full_status_flow(self):
        self.pickup.status = 'dijadwalkan'
        self.pickup.petugas = self.petugas
        self.pickup.save()

        self.auth_as(self.petugas)
        for new_status in ('dalam_perjalanan', 'dijemput', 'selesai'):
            response = self.client.patch(
                f'/api/pickups/{self.pickup.id}/',
                {'status': new_status},
                format='json',
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK, new_status)
            self.assertEqual(response.data['data']['status'], new_status)
            self.pickup.refresh_from_db()

    def test_invalid_transition_returns_409(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['code'], 'INVALID_STATUS_TRANSITION')

    def test_petugas_cannot_update_unassigned(self):
        self.pickup.status = 'dijadwalkan'
        self.pickup.petugas = self.petugas
        self.pickup.save()

        self.auth_as(self.other_petugas)
        response = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'dalam_perjalanan'},
            format='json',
        )
        self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    def test_petugas_cannot_approve(self):
        self.auth_as(self.petugas)
        response = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'disetujui'},
            format='json',
        )
        self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    def test_schedule_requires_petugas(self):
        self.pickup.status = 'disetujui'
        self.pickup.save()
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'dijadwalkan'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_petugas_list_hides_menunggu_and_unassigned(self):
        waiting = self.pickup
        assigned = Penjemputan.objects.create(
            nasabah=self.nasabah,
            petugas=self.petugas,
            estimasi_berat=Decimal('6.00'),
            alamat_jemput='Timika 2',
            jadwal=timezone.now() + timedelta(days=4),
            status='dijadwalkan',
        )
        done = Penjemputan.objects.create(
            nasabah=self.nasabah,
            petugas=self.petugas,
            estimasi_berat=Decimal('6.50'),
            alamat_jemput='Timika 2b',
            jadwal=timezone.now() - timedelta(days=1),
            status='selesai',
        )
        Penjemputan.objects.create(
            nasabah=self.nasabah,
            petugas=self.other_petugas,
            estimasi_berat=Decimal('7.00'),
            alamat_jemput='Timika 3',
            jadwal=timezone.now() + timedelta(days=5),
            status='dijadwalkan',
        )
        rejected = Penjemputan.objects.create(
            nasabah=self.nasabah,
            estimasi_berat=Decimal('8.00'),
            alamat_jemput='Timika 4',
            jadwal=timezone.now() + timedelta(days=6),
            status='ditolak',
        )

        self.auth_as(self.petugas)
        response = self.client.get('/api/pickups/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row['id'] for row in response.data['data']}
        self.assertIn(assigned.id, ids)
        self.assertIn(done.id, ids)
        self.assertNotIn(waiting.id, ids)
        self.assertNotIn(rejected.id, ids)
        statuses = {row['status'] for row in response.data['data']}
        self.assertNotIn('menunggu', statuses)
        self.assertNotIn('ditolak', statuses)
        self.assertIn('selesai', statuses)

        selesai_tab = self.client.get('/api/pickups/?status=selesai')
        self.assertEqual(selesai_tab.status_code, status.HTTP_200_OK)
        selesai_ids = {row['id'] for row in selesai_tab.data['data']}
        self.assertEqual(selesai_ids, {done.id})

    def test_filter_by_status(self):
        self.pickup.status = 'ditolak'
        self.pickup.save()
        self.auth_as(self.admin)
        response = self.client.get('/api/pickups/?status=ditolak')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_filter_by_status_in(self):
        """Tab Aktif admin memakai ?status__in=disetujui,dijadwalkan,..."""
        self.pickup.status = 'disetujui'
        self.pickup.petugas = self.petugas
        self.pickup.save()
        Penjemputan.objects.create(
            nasabah=self.nasabah,
            estimasi_berat=Decimal('6.00'),
            alamat_jemput='Timika 2',
            jadwal=timezone.now() + timedelta(days=4),
            status='menunggu',
        )
        self.auth_as(self.admin)
        response = self.client.get(
            '/api/pickups/?status__in=disetujui,dijadwalkan,dalam_perjalanan,dijemput',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        statuses = {row['status'] for row in response.data['data']}
        self.assertIn('disetujui', statuses)
        self.assertNotIn('menunggu', statuses)

    def test_nasabah_cannot_update(self):
        self.auth_as(self.nasabah)
        response = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'disetujui'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PickupActionTests(EnvelopeAPITestCase):
    """SOP B.2 — action endpoints approve/reject/assign/update-status."""

    def setUp(self):
        self.nasabah = self.create_nasabah(username='nasabah_action')
        self.petugas = self.create_petugas(username='petugas_action')
        self.admin = self.create_admin(username='admin_action')
        self.pickup = Penjemputan.objects.create(
            nasabah=self.nasabah,
            estimasi_berat=Decimal('10.00'),
            alamat_jemput='Timika',
            jadwal=timezone.now() + timedelta(days=3),
            status='menunggu',
        )

    def test_approve_without_petugas_rejected(self):
        self.auth_as(self.admin)
        response = self.client.post(f'/api/pickups/{self.pickup.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_action_atomic_with_petugas(self):
        self.auth_as(self.admin)
        response = self.client.post(
            f'/api/pickups/{self.pickup.id}/approve/',
            {'petugas_id': self.petugas.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'dijadwalkan')
        self.assertEqual(response.data['data']['petugas'], self.petugas.id)

    def test_reject_action(self):
        self.auth_as(self.admin)
        response = self.client.post(f'/api/pickups/{self.pickup.id}/reject/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'ditolak')

    def test_assign_action(self):
        self.pickup.status = 'disetujui'
        self.pickup.save()
        self.auth_as(self.admin)
        response = self.client.post(
            f'/api/pickups/{self.pickup.id}/assign/',
            {'petugas_id': self.petugas.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'dijadwalkan')
        self.assertEqual(response.data['data']['petugas'], self.petugas.id)

    def test_assign_sends_notifications_to_nasabah_and_petugas(self):
        self.auth_as(self.admin)
        response = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'dijadwalkan', 'petugas': self.petugas.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        nasabah_notif = Notifikasi.objects.filter(
            user=self.nasabah, kategori='penjemputan',
        ).order_by('-created_at').first()
        self.assertIsNotNone(nasabah_notif)
        self.assertIn('sudah disetujui', nasabah_notif.deskripsi.lower())
        self.assertIn('dijemput oleh petugas', nasabah_notif.deskripsi.lower())

        petugas_notif = Notifikasi.objects.filter(
            user=self.petugas, kategori='penjemputan',
        ).order_by('-created_at').first()
        self.assertIsNotNone(petugas_notif)
        self.assertIn('mendapat tugas menjemput', petugas_notif.deskripsi.lower())

    def test_selesai_notifies_petugas_and_admin(self):
        self.pickup.status = 'dijemput'
        self.pickup.petugas = self.petugas
        self.pickup.save()

        self.auth_as(self.petugas)
        before_petugas = Notifikasi.objects.filter(user=self.petugas).count()
        before_admin = Notifikasi.objects.filter(user=self.admin).count()
        response = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'selesai'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            Notifikasi.objects.filter(user=self.petugas).count(),
            before_petugas + 1,
        )
        self.assertEqual(
            Notifikasi.objects.filter(user=self.admin).count(),
            before_admin + 1,
        )
        admin_notif = Notifikasi.objects.filter(
            user=self.admin, judul='Penjemputan Selesai',
        ).order_by('-created_at').first()
        self.assertIsNotNone(admin_notif)
        self.assertIn(str(self.pickup.id), admin_notif.deskripsi)

    def test_each_status_change_notifies_nasabah(self):
        self.pickup.status = 'dijadwalkan'
        self.pickup.petugas = self.petugas
        self.pickup.save()

        expected = {
            'dalam_perjalanan': 'dalam perjalanan',
            'dijemput': 'dijemput',
            'selesai': 'selesai',
        }
        self.auth_as(self.petugas)
        for new_status, keyword in expected.items():
            before = Notifikasi.objects.filter(user=self.nasabah).count()
            response = self.client.patch(
                f'/api/pickups/{self.pickup.id}/',
                {'status': new_status},
                format='json',
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK, new_status)
            after = Notifikasi.objects.filter(user=self.nasabah).count()
            self.assertEqual(after, before + 1, new_status)
            latest = Notifikasi.objects.filter(
                user=self.nasabah, kategori='penjemputan',
            ).order_by('-created_at').first()
            self.assertIsNotNone(latest)
            self.assertIn(keyword, latest.deskripsi.lower() + latest.judul.lower())

    def test_update_status_action(self):
        self.pickup.status = 'dijadwalkan'
        self.pickup.petugas = self.petugas
        self.pickup.save()
        self.auth_as(self.petugas)
        response = self.client.post(
            f'/api/pickups/{self.pickup.id}/update-status/',
            {'status': 'dalam_perjalanan'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'dalam_perjalanan')

    def test_petugas_cannot_approve_action(self):
        self.auth_as(self.petugas)
        response = self.client.post(
            f'/api/pickups/{self.pickup.id}/approve/',
            {'petugas_id': self.petugas.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_e2e_full_flow_via_actions(self):
        self.auth_as(self.admin)
        approve = self.client.post(
            f'/api/pickups/{self.pickup.id}/approve/',
            {'petugas_id': self.petugas.id},
            format='json',
        )
        self.assertEqual(approve.status_code, status.HTTP_200_OK)
        self.assertEqual(approve.data['data']['status'], 'dijadwalkan')

        self.auth_as(self.petugas)
        for next_status in ('dalam_perjalanan', 'dijemput', 'selesai'):
            response = self.client.post(
                f'/api/pickups/{self.pickup.id}/update-status/',
                {'status': next_status},
                format='json',
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK, next_status)
            self.assertEqual(response.data['data']['status'], next_status)

        self.pickup.refresh_from_db()
        self.assertEqual(self.pickup.status, 'selesai')
