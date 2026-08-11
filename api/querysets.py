"""Reusable queryset filters per role."""

READ_ALL_ROLES = ('admin', 'koordinator', 'pemerintah')
OPERATIONAL_WRITE_ROLES = ('admin', 'petugas')
KOORDINATOR_APPROVE_ROLES = ('admin', 'koordinator')


def filter_nasabah_owned(qs, user, nasabah_field: str = 'nasabah'):
    """Nasabah sees own data; staff roles see all."""
    if user.role == 'nasabah':
        return qs.filter(**{nasabah_field: user})
    if user.role in READ_ALL_ROLES:
        return qs
    if user.role == 'petugas':
        return qs
    return qs.none()


def filter_pickup_queryset(qs, user):
    if user.role == 'nasabah':
        return qs.filter(nasabah=user)
    if user.role == 'petugas':
        # Petugas: hanya jemput yang ditugaskan ke diri sendiri;
        # sembunyikan menunggu/ditolak (dan status tanpa tugas aktif).
        from api.services.pickups import PETUGAS_VISIBLE_STATUSES
        return qs.filter(petugas=user, status__in=PETUGAS_VISIBLE_STATUSES)
    if user.role in READ_ALL_ROLES:
        return qs
    return qs.none()


def filter_staff_only(qs, user):
    """Admin/koordinator/pemerintah read; others denied."""
    if user.role in READ_ALL_ROLES:
        return qs
    return qs.none()
