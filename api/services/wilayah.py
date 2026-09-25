"""Cakupan wilayah layanan MIRU: hanya Distrik Mimika Baru.

Kode & nama mengikuti Kepmendagri (sumber: API wilayah.id, data 2025-07-04).
Alamat dipilih bertingkat provinsi → kabupaten → distrik → kelurahan/kampung;
tiga tingkat pertama dikunci ke satu pilihan, kelurahan/kampung memakai
tabel `WilayahLayanan` (lihat `sync_wilayah` untuk memperbarui dari API).
"""

from __future__ import annotations

WILAYAH_API_BASE = 'https://wilayah.id/api'

PROVINSI = {'kode': '94', 'nama': 'Papua Tengah'}
KABUPATEN = {'kode': '94.04', 'nama': 'Kabupaten Mimika'}
DISTRIK = {'kode': '94.04.01', 'nama': 'Mimika Baru'}

PESAN_CAKUPAN = (
    'MIRU Bank Sampah hanya melayani warga Distrik Mimika Baru, '
    'Kabupaten Mimika, Papua Tengah.'
)

# Kode Kemendagri: 1xxx = kelurahan, 2xxx = kampung (desa).
KELURAHAN_MIMIKA_BARU = [
    ('94.04.01.1001', 'Koperapoka'),
    ('94.04.01.1002', 'Kwamki'),
    ('94.04.01.1003', 'Timika Jaya'),
    ('94.04.01.1007', 'Sempan'),
    ('94.04.01.1008', 'Pasar Sentral'),
    ('94.04.01.1009', 'Wanagon'),
    ('94.04.01.1010', 'Kebun Sirih'),
    ('94.04.01.1011', 'Otomona'),
    ('94.04.01.1012', 'Perintis'),
    ('94.04.01.1013', 'Dingo Narama'),
    ('94.04.01.1014', 'Timika Indah'),
    ('94.04.01.2004', 'Nayaro'),
    ('94.04.01.2005', 'Minabua'),
    ('94.04.01.2006', 'Hangaitji'),
]

# Kotak kasar sekitar Timika untuk membatasi geser peta (bukan batas resmi —
# OpenStreetMap belum punya poligon Distrik Mimika Baru).
PETA = {
    'pusat': {'lat': -4.5467, 'lng': 136.8833},
    'batas': {'selatan': -4.70, 'barat': 136.65, 'utara': -4.25, 'timur': 137.05},
    'zoom': 13,
}


def jenis_dari_kode(kode: str) -> str:
    return 'kampung' if kode.rsplit('.', 1)[-1].startswith('2') else 'kelurahan'


def upsert_kelurahan(model, items):
    """Buat/perbarui wilayah resmi berdasarkan kode; cocokkan nama lama tanpa kode.

    Mengembalikan jumlah baris yang dibuat. `model` diteruskan agar bisa dipakai
    dari data migration (model historis).
    """
    created = 0
    for kode, nama in items:
        obj = model.objects.filter(kode=kode).first()
        if obj is None:
            obj = model.objects.filter(
                kode__isnull=True, kelurahan__iexact=nama, rt='', rw='',
            ).first()
        if obj is None:
            obj = model(kode=kode)
            created += 1
        obj.kode = kode
        obj.kelurahan = nama
        obj.jenis = jenis_dari_kode(kode)
        obj.aktif = True
        obj.save()
    return created


def payload_cakupan(kelurahan_qs) -> dict:
    return {
        'provinsi': PROVINSI,
        'kabupaten': KABUPATEN,
        'distrik': DISTRIK,
        'kelurahan': [
            {'id': w.id, 'kode': w.kode, 'nama': w.kelurahan, 'jenis': w.jenis}
            for w in kelurahan_qs
        ],
        'pesan': PESAN_CAKUPAN,
        'peta': PETA,
    }
