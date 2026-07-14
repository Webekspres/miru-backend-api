"""
Locust load test untuk MIRU Bank Sampah API.

Cara pakai:
    # Install locust
    pip install locust

    # Jalankan dengan Web UI
    locust -f scripts/locustfile.py --host=http://localhost:8000

    # Jalankan headless (50 users, 10 spawn rate, 5 menit)
    locust -f scripts/locustfile.py --host=http://localhost:8000 \\
        --users=50 --spawn-rate=10 --run-time=5m --headless

Prerequisites:
    - Server API berjalan (lokal: `python manage.py runserver`)
    - Seed data sudah di-load (`python manage.py seed_data`)
"""

import random
from locust import HttpUser, task, between, constant


# Akun demo dari seed_data
NASABAH_ACCOUNTS = [
    {'username': 'nasabah001', 'password': 'nasabah123'},
    {'username': 'nasabah002', 'password': 'nasabah123'},
    {'username': 'nasabah003', 'password': 'nasabah123'},
]

PETUGAS_ACCOUNT = {'username': 'petugas1', 'password': 'petugas123'}

ADMIN_ACCOUNT = {'username': 'admin', 'password': 'admin123'}


class NasabahUser(HttpUser):
    """
    Simulasi nasabah — aktivitas baca (cek saldo, lihat riwayat).
    ~70% dari total traffic.
    """
    wait_time = between(2, 8)  # tunggu 2-8 detik antar request
    weight = 7

    def on_start(self):
        """Login sebagai nasabah random."""
        creds = random.choice(NASABAH_ACCOUNTS)
        resp = self.client.post('/api/auth/login/', json={
            'username': creds['username'],
            'password': creds['password'],
        })
        if resp.status_code == 200:
            data = resp.json()
            self.token = data['data']['access']
            self.user_id = data['data']['user']['id']
            self.client.headers.update({
                'Authorization': f'Bearer {self.token}',
            })
        else:
            self.token = None

    def on_stop(self):
        """Cleanup."""
        self.client.headers.pop('Authorization', None)

    @task(5)
    def view_profile(self):
        """Cek profil & saldo sendiri."""
        if not self.token:
            return
        self.client.get('/api/auth/me/')

    @task(3)
    def view_deposits(self):
        """Lihat riwayat setoran."""
        if not self.token:
            return
        self.client.get(f'/api/deposits/?nasabah={self.user_id}')

    @task(3)
    def view_pickups(self):
        """Lihat status penjemputan."""
        if not self.token:
            return
        self.client.get(f'/api/pickups/?nasabah={self.user_id}')

    @task(2)
    def view_withdrawals(self):
        """Lihat riwayat penarikan."""
        if not self.token:
            return
        self.client.get(f'/api/withdrawals/?nasabah={self.user_id}')

    @task(2)
    def view_rewards(self):
        """Lihat katalog reward."""
        if not self.token:
            return
        self.client.get('/api/rewards/')

    @task(2)
    def view_complaints(self):
        """Lihat pengaduan sendiri."""
        if not self.token:
            return
        self.client.get(f'/api/complaints/?nasabah={self.user_id}')

    @task(1)
    def view_waste_categories(self):
        """Lihat kategori & harga sampah (public)."""
        self.client.get('/api/waste-categories/')

    @task(1)
    def view_activity(self):
        """Lihat riwayat transaksi gabungan."""
        if not self.token:
            return
        self.client.get('/api/activity/')

    @task(1)
    def view_notifications(self):
        """Lihat notifikasi."""
        if not self.token:
            return
        self.client.get('/api/notifications/')

    @task(1)
    def health_check(self):
        """Health check endpoint (public)."""
        self.client.get('/health/')


class PetugasUser(HttpUser):
    """
    Simulasi petugas — aktivitas write (input setoran).
    ~20% dari total traffic.
    """
    wait_time = between(3, 10)
    weight = 2

    def on_start(self):
        """Login sebagai petugas."""
        resp = self.client.post('/api/auth/login/', json={
            'username': PETUGAS_ACCOUNT['username'],
            'password': PETUGAS_ACCOUNT['password'],
        })
        if resp.status_code == 200:
            data = resp.json()
            self.token = data['data']['access']
            self.client.headers.update({
                'Authorization': f'Bearer {self.token}',
            })
            # Ambil nasabah random dan kategori untuk write operations
            self._load_references()
        else:
            self.token = None

    def _load_references(self):
        """Load referensi data (nasabah, kategori) untuk write."""
        if not self.token:
            return
        resp = self.client.get('/api/users/?role=nasabah&page_size=5')
        if resp.status_code == 200:
            data = resp.json()
            self.nasabah_ids = [u['id'] for u in data.get('data', [])]
        else:
            self.nasabah_ids = [1]

        resp = self.client.get('/api/waste-categories/')
        if resp.status_code == 200:
            data = resp.json()
            self.kategori_list = data.get('data', [])
        else:
            self.kategori_list = [{'id': 1, 'nama': 'Kertas'}]

    @task(3)
    def input_deposit(self):
        """Input setoran sampah (write operation)."""
        if not self.token or not self.nasabah_ids:
            return
        nasabah_id = random.choice(self.nasabah_ids)
        kategori = random.choice(self.kategori_list)
        berat = round(random.uniform(1.0, 10.0), 2)
        self.client.post('/api/deposits/', json={
            'nasabah': nasabah_id,
            'details': [{'kategori': kategori['id'], 'berat_kg': str(berat)}],
        })

    @task(2)
    def update_pickup_status(self):
        """Update status penjemputan."""
        if not self.token:
            return
        # Ambil pickup yang dijadwalkan
        resp = self.client.get('/api/pickups/?status=dijadwalkan&page_size=1')
        if resp.status_code == 200:
            pickups = resp.json().get('data', [])
            if pickups:
                pickup = pickups[0]
                self.client.patch(
                    f"/api/pickups/{pickup['id']}/",
                    json={'status': 'dalam_perjalanan'},
                )

    @task(1)
    def view_assigned_pickups(self):
        """Lihat penjemputan yang ditugaskan."""
        if not self.token:
            return
        self.client.get('/api/pickups/')


class AdminUser(HttpUser):
    """
    Simulasi admin — aktivitas berat (dashboard, laporan).
    ~10% dari total traffic.
    """
    wait_time = between(5, 15)
    weight = 1

    def on_start(self):
        """Login sebagai admin."""
        resp = self.client.post('/api/auth/login/', json={
            'username': ADMIN_ACCOUNT['username'],
            'password': ADMIN_ACCOUNT['password'],
        })
        if resp.status_code == 200:
            data = resp.json()
            self.token = data['data']['access']
            self.client.headers.update({
                'Authorization': f'Bearer {self.token}',
            })
        else:
            self.token = None

    @task(3)
    def view_dashboard(self):
        """Lihat dashboard overview — query aggregat berat."""
        if not self.token:
            return
        self.client.get('/api/dashboard/overview/')

    @task(2)
    def view_deposit_chart(self):
        """Lihat chart setoran."""
        if not self.token:
            return
        self.client.get('/api/dashboard/deposit-chart/')

    @task(2)
    def view_daily_report(self):
        """Laporan harian."""
        if not self.token:
            return
        self.client.get('/api/reports/daily/')

    @task(1)
    def view_monthly_report(self):
        """Laporan bulanan — query berat."""
        if not self.token:
            return
        self.client.get('/api/reports/monthly/')

    @task(2)
    def view_inventory(self):
        """Lihat stok gudang."""
        if not self.token:
            return
        self.client.get('/api/inventory/')

    @task(1)
    def view_users(self):
        """Lihat daftar user."""
        if not self.token:
            return
        self.client.get('/api/users/')

    @task(1)
    def view_audit_log(self):
        """Lihat audit log."""
        if not self.token:
            return
        self.client.get('/api/audit-log/')

    @task(1)
    def view_all_deposits(self):
        """Lihat semua setoran (staff only)."""
        if not self.token:
            return
        self.client.get('/api/deposits/')


class AnonymousUser(HttpUser):
    """
    Simulasi anonymous — akses endpoint publik.
    ~5% dari total traffic.
    """
    wait_time = between(1, 3)
    weight = 0.5

    @task(3)
    def health_check(self):
        self.client.get('/health/')

    @task(2)
    def waste_categories(self):
        self.client.get('/api/waste-categories/')

    @task(1)
    def login_failed(self):
        """Request login gagal — hit 401."""
        self.client.post('/api/auth/login/', json={
            'username': 'nonexistent',
            'password': 'wrong',
        })
