"""Reusable queryset filters per role."""

READ_ALL_ROLES = ('admin', 'koordinator', 'pemerintah')
OPERATIONAL_WRITE_ROLES = ('admin', 'petugas')
KOORDINATOR_APPROVE_ROLES = ('admin', 'koordinator')


def filter_nasabah_owned(qs, user, nasabah_field: str = 'nasabah'):
    """Nasabah sees own data; staff roles see all; petugas sees own operational rows."""
    if user.role == 'nasabah':
        return qs.filter(**{nasabah_field: user})
    if user.role in READ_ALL_ROLES:
        return qs
    if user.role == 'petugas':
        # Setoran dll. yang punya FK petugas → hanya riwayat milik petugas itu.
        field_names = {f.name for f in qs.model._meta.get_fields()}
        if 'petugas' in field_names:
            return qs.filter(petugas=user)
        return qs
    return qs.none()


def filter_pickup_queryset(qs, user):
    if user.role == 'nasabah':
        return qs.filter(nasabah=user)
    if user.role == 'petugas':
        # Ditugaskan ke petugas ini; termasuk selesai (tab Selesai).
        # Sembunyikan antrian menunggu/ditolak (bukan tugas petugas).
        return qs.filter(petugas=user).exclude(status__in=('menunggu', 'ditolak'))
    if user.role in READ_ALL_ROLES:
        return qs
    return qs.none()


def filter_staff_only(qs, user):
    """Admin/koordinator/pemerintah read; others denied."""
    if user.role in READ_ALL_ROLES:
        return qs
    return qs.none()
