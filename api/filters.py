import django_filters

from api.models import TransaksiSetoran


class TransaksiSetoranFilter(django_filters.FilterSet):
    tanggal_after = django_filters.DateFilter(field_name='tanggal', lookup_expr='date__gte')
    tanggal_before = django_filters.DateFilter(field_name='tanggal', lookup_expr='date__lte')

    class Meta:
        model = TransaksiSetoran
        fields = ['nasabah', 'status']
