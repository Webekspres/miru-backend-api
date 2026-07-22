import django_filters

from api.models import Penjemputan, TransaksiSetoran


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class TransaksiSetoranFilter(django_filters.FilterSet):
    tanggal_after = django_filters.DateFilter(field_name='tanggal', lookup_expr='date__gte')
    tanggal_before = django_filters.DateFilter(field_name='tanggal', lookup_expr='date__lte')

    class Meta:
        model = TransaksiSetoran
        fields = ['nasabah', 'status']


class PenjemputanFilter(django_filters.FilterSet):
    """Supports ?status=menunggu and ?status__in=disetujui,dijadwalkan,..."""

    status = django_filters.CharFilter(field_name='status')
    status__in = CharInFilter(field_name='status', lookup_expr='in')

    class Meta:
        model = Penjemputan
        fields = ['nasabah', 'status', 'petugas']
