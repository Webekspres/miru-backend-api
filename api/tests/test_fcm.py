"""Tests for FCM device tokens and safe payloads (Fase 8.6)."""

from unittest.mock import patch

from django.test import override_settings

from api.models import DeviceToken, Notifikasi, Pengumuman
from api.services.fcm import build_notification_payload, sanitize_fcm_data
from api.services.notifications import create_notification
from api.tests.base import EnvelopeAPITestCase


class FcmPayloadSanitizationTests(EnvelopeAPITestCase):
    def test_allowlist_only(self):
        safe = sanitize_fcm_data({
            'kategori': 'penarikan',
            'notification_id': 12,
            'nik': '1234567890123456',
            'access_token': 'secret-jwt',
            'extra': 'drop-me',
        })
        self.assertEqual(safe, {
            'kategori': 'penarikan',
            'notification_id': '12',
        })
        self.assertNotIn('nik', safe)
        self.assertNotIn('access_token', safe)

    def test_forbidden_value_dropped(self):
        safe = sanitize_fcm_data({
            'kategori': 'setoran',
            'event': 'Bearer abc.def.ghi',
        })
        self.assertEqual(safe, {'kategori': 'setoran'})

    def test_build_payload_defaults(self):
        payload = build_notification_payload(
            kategori='penjemputan',
            notification_id=5,
            event='penjemputan',
        )
        self.assertEqual(payload['kategori'], 'penjemputan')
        self.assertEqual(payload['notification_id'], '5')
        self.assertEqual(payload['event'], 'penjemputan')


class DeviceTokenAPITests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah()
        self.other = self.create_nasabah(username='other_nasabah')
        self.token_value = 'a' * 40  # fake FCM-looking token

    def test_register_device_token(self):
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/device-tokens/',
            {'token': self.token_value, 'platform': 'android'},
            format='json',
        )
        self.assert_envelope_success(response, 201)
        self.assertTrue(
            DeviceToken.objects.filter(
                user=self.nasabah, token=self.token_value,
            ).exists()
        )

    def test_reassign_token_to_current_user(self):
        DeviceToken.objects.create(
            user=self.other, token=self.token_value, platform='android',
        )
        self.auth_as(self.nasabah)
        response = self.client.post(
            '/api/device-tokens/',
            {'token': self.token_value, 'platform': 'ios'},
            format='json',
        )
        self.assert_envelope_success(response, 200)
        obj = DeviceToken.objects.get(token=self.token_value)
        self.assertEqual(obj.user_id, self.nasabah.id)
        self.assertEqual(obj.platform, 'ios')

    def test_list_only_own_tokens(self):
        DeviceToken.objects.create(
            user=self.nasabah, token=self.token_value, platform='android',
        )
        DeviceToken.objects.create(
            user=self.other, token='b' * 40, platform='android',
        )
        self.auth_as(self.nasabah)
        response = self.client.get('/api/device-tokens/')
        self.assert_envelope_success(response, 200)
        self.assertEqual(len(response.data['data']), 1)

    def test_unregister_by_token(self):
        DeviceToken.objects.create(
            user=self.nasabah, token=self.token_value, platform='android',
        )
        self.auth_as(self.nasabah)
        response = self.client.delete(
            '/api/device-tokens/unregister/',
            {'token': self.token_value},
            format='json',
        )
        self.assert_envelope_success(response, 200)
        self.assertFalse(
            DeviceToken.objects.filter(token=self.token_value).exists()
        )

    def test_cannot_delete_others_token_by_pk(self):
        obj = DeviceToken.objects.create(
            user=self.other, token=self.token_value, platform='android',
        )
        self.auth_as(self.nasabah)
        response = self.client.delete(f'/api/device-tokens/{obj.pk}/')
        self.assert_envelope_error(response, 404)
        self.assertTrue(DeviceToken.objects.filter(pk=obj.pk).exists())

    def test_unauthenticated_rejected(self):
        response = self.client.post(
            '/api/device-tokens/',
            {'token': self.token_value},
            format='json',
        )
        self.assertIn(response.status_code, (401, 403))


class FcmTriggerTests(EnvelopeAPITestCase):
    def setUp(self):
        self.nasabah = self.create_nasabah()
        DeviceToken.objects.create(
            user=self.nasabah,
            token='c' * 40,
            platform='android',
        )

    @override_settings(FCM_ENABLED=False)
    @patch('api.services.fcm.send_to_user')
    def test_create_notification_triggers_fcm(self, mock_send):
        mock_send.return_value = 1
        notif = create_notification(
            user_id=self.nasabah.id,
            judul='Penarikan Disetujui',
            deskripsi='Saldo sudah diproses.',
            kategori='penarikan',
        )
        mock_send.assert_called_once()
        kwargs = mock_send.call_args
        self.assertEqual(kwargs[0][0], self.nasabah.id)
        self.assertEqual(kwargs[1]['title'], 'Penarikan Disetujui')
        data = kwargs[1]['data']
        self.assertEqual(data['kategori'], 'penarikan')
        self.assertEqual(data['notification_id'], str(notif.id))
        self.assertNotIn('nik', data)

    @override_settings(FCM_ENABLED=False)
    @patch('api.services.fcm.send_to_user_ids')
    def test_pengumuman_broadcast_triggers_fcm(self, mock_send):
        mock_send.return_value = 1
        Pengumuman.objects.create(
            judul='Jadwal Libur',
            isi='Kantor tutup hari Jumat.',
            aktif=True,
        )
        mock_send.assert_called_once()
        self.assertTrue(
            Notifikasi.objects.filter(
                user=self.nasabah, kategori='pengumuman',
            ).exists()
        )
        data = mock_send.call_args[1]['data']
        self.assertEqual(data['kategori'], 'pengumuman')
        self.assertNotIn('nik', data)

    @override_settings(FCM_ENABLED=False)
    @patch('api.services.fcm.send_to_user_ids')
    def test_harga_pengumuman_uses_harga_kategori(self, mock_send):
        mock_send.return_value = 1
        Pengumuman.objects.create(
            judul='Perubahan Harga Plastik PET',
            isi='Harga jadi Rp3000/kg.',
            aktif=True,
        )
        self.assertTrue(
            Notifikasi.objects.filter(
                user=self.nasabah, kategori='harga',
            ).exists()
        )
        data = mock_send.call_args[1]['data']
        self.assertEqual(data['kategori'], 'harga')
