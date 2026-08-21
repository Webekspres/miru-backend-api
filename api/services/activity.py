"""Merged transaction history for nasabah activity feed."""

from rest_framework.exceptions import ValidationError

from api.models import PenarikanSaldo, PenukaranPoin, TransaksiSetoran, User
from api.querysets import filter_nasabah_owned

VALID_JENIS = frozenset({'setoran', 'penarikan', 'poin'})

JENIS_TO_TYPES = {
    'setoran': {'setoran'},
    'penarikan': {'penarikan'},
    'poin': {'penukaran_poin'},
}

ALL_TYPES = {'setoran', 'penarikan', 'penukaran_poin'}


def _types_for_jenis(jenis: str | None) -> set[str]:
    if not jenis:
        return ALL_TYPES
    if jenis not in VALID_JENIS:
        raise ValidationError({'jenis': ['Nilai tidak valid. Gunakan: setoran, penarikan, poin.']})
    return JENIS_TO_TYPES[jenis]


def _resolve_nasabah_filter(user: User, nasabah_id: str | None) -> int | None:
    if user.role == 'nasabah':
        return user.pk
    if nasabah_id:
        try:
            return int(nasabah_id)
        except (TypeError, ValueError) as exc:
            raise ValidationError({'nasabah': ['ID nasabah tidak valid.']}) from exc
    return None


def _setoran_items(qs) -> list[dict]:
    items = []
    for row in qs.select_related('petugas').prefetch_related('details__kategori'):
        details = [
            {
                'id': d.id,
                'kategori': d.kategori_id,
                'kategori_nama': d.kategori.nama,
                'berat_kg': f'{d.berat_kg:.2f}',
                'harga_saat_itu': f'{d.harga_saat_itu:.2f}',
                'subtotal': f'{d.subtotal:.2f}',
            }
            for d in row.details.all()
        ]
        petugas_nama = None
        if row.petugas_id and row.petugas is not None:
            petugas_nama = row.petugas.nama_lengkap
        items.append({
            '_sort_tanggal': row.tanggal,
            'id': row.id,
            'type': 'setoran',
            'nominal': f'{row.total_nilai:.2f}',
            'status': row.status,
            'keterangan': f'Setoran {len(details)} jenis sampah',
            'petugas': row.petugas_id,
            'petugas_nama': petugas_nama,
            'details': details,
        })
    return items


def _penarikan_items(qs) -> list[dict]:
    return [
        {
            '_sort_tanggal': row.tanggal,
            'id': row.id,
            'type': 'penarikan',
            'nominal': f'{row.nominal:.2f}',
            'status': row.status,
            'keterangan': f'Penarikan {row.metode}',
        }
        for row in qs
    ]


def _penukaran_items(qs) -> list[dict]:
    return [
        {
            '_sort_tanggal': row.tanggal,
            'id': row.id,
            'type': 'penukaran_poin',
            'nominal': None,
            'poin': row.poin_dibutuhkan,
            'status': row.status,
            'keterangan': row.reward.nama,
        }
        for row in qs.select_related('reward')
    ]


def get_activity_items(
    user: User,
    *,
    jenis: str | None = None,
    nasabah_id: str | None = None,
    ordering: str = '-tanggal',
) -> list[dict]:
    types = _types_for_jenis(jenis)
    nasabah_filter = _resolve_nasabah_filter(user, nasabah_id)

    if ordering not in ('tanggal', '-tanggal'):
        raise ValidationError({'ordering': ['Hanya ordering tanggal yang didukung.']})

    items: list[dict] = []

    if 'setoran' in types:
        qs = filter_nasabah_owned(TransaksiSetoran.objects.all(), user)
        if nasabah_filter is not None:
            qs = qs.filter(nasabah_id=nasabah_filter)
        items.extend(_setoran_items(qs))

    if 'penarikan' in types:
        qs = filter_nasabah_owned(PenarikanSaldo.objects.all(), user)
        if nasabah_filter is not None:
            qs = qs.filter(nasabah_id=nasabah_filter)
        items.extend(_penarikan_items(qs))

    if 'penukaran_poin' in types:
        qs = filter_nasabah_owned(PenukaranPoin.objects.all(), user)
        if nasabah_filter is not None:
            qs = qs.filter(nasabah_id=nasabah_filter)
        items.extend(_penukaran_items(qs))

    reverse = ordering.startswith('-')
    items.sort(key=lambda row: row['_sort_tanggal'], reverse=reverse)

    for row in items:
        row['tanggal'] = row.pop('_sort_tanggal').isoformat()

    return items
