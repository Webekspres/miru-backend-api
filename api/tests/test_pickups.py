from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework import status

from api.models import Penjemputan

from .base import EnvelopeAPITestCase


class PickupCreateTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah(username='nasabah_pickup')
        self.petugas = self.create_petugas()
        self.admin = self.create_admin(username='admin_pickup')
        self.jadwal = (timezone.now() + timedelta(days=2)).replace(
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

    def test_reject_weight_below_5kg(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/pickups/',
            self._payload(estimasi_berat='4.00'),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_jadwal_today(self):
        self.auth_as(self.nasabah)
        today = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0)
        response = self.client.post(
            '/api/pickups/',
            self._payload(jadwal=today.isoformat()),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_admin_approve_and_schedule(self):
        self.auth_as(self.admin)
        approve = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'disetujui'},
            format='json',
        )
        self.assertEqual(approve.status_code, status.HTTP_200_OK)

        schedule = self.client.patch(
            f'/api/pickups/{self.pickup.id}/',
            {'status': 'dijadwalkan', 'petugas': self.petugas.id},
            format='json',
        )
        self.assertEqual(schedule.status_code, status.HTTP_200_OK)
        self.assertEqual(schedule.data['data']['status'], 'dijadwalkan')
        self.assertEqual(schedule.data['data']['petugas'], self.petugas.id)

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

    def test_approve_action(self):
        self.auth_as(self.admin)
        response = self.client.post(f'/api/pickups/{self.pickup.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'disetujui')

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
        from api.models import Notifikasi

        self.pickup.status = 'disetujui'
        self.pickup.save()
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

    def test_each_status_change_notifies_nasabah(self):
        from api.models import Notifikasi

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
        response = self.client.post(f'/api/pickups/{self.pickup.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_e2e_full_flow_via_actions(self):
        self.auth_as(self.admin)
        self.client.post(f'/api/pickups/{self.pickup.id}/approve/')
        self.client.post(
            f'/api/pickups/{self.pickup.id}/assign/',
            {'petugas_id': self.petugas.id},
            format='json',
        )

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
