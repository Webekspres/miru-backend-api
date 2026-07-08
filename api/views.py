from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from .filters import TransaksiSetoranFilter
from .models import *
from .querysets import filter_nasabah_owned, filter_pickup_queryset, filter_staff_only
from .services import (
    complete_penukaran_poin,
    debit_nasabah_saldo,
)
from .services.pickups import (
    approve_pickup,
    assign_pickup,
    reject_pickup,
    update_pickup_status,
)
from .services.withdrawals import approve_withdrawal, reject_withdrawal
from .services.redemptions import approve_redemption
from .services.activity import get_activity_items
from .openapi import (
    ACTIVITY_TAG,
    complaint_schema,
    deposit_schema,
    partner_sale_schema,
    partner_schema,
    pickup_schema,
    redemption_schema,
    reward_schema,
    user_viewset_schema,
    waste_category_schema,
    withdrawal_schema,
)
from .permissions import (
    IsActivityReader,
    IsAdmin,
    IsAdminOrKoordinator,
    IsNasabah,
    IsOwnerOrAdmin,
    IsPemerintahReadOnly,
    IsPetugasOrAdmin,
    IsPickupManager,
    IsMonitorReadOnly,
    IsStaffManagerOrPetugas,
    IsUserOwnerOrAdmin,
)
from .serializers import *
from .utils.pagination import MiruPagination
from .utils.response import success_response


@user_viewset_schema
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAdminOrKoordinator]
    search_fields = ['username', 'nama_lengkap', 'no_hp', 'nik']
    filterset_fields = ['role', 'is_active']
    ordering_fields = ['date_joined', 'nama_lengkap', 'username']
    ordering = ['-date_joined']

    def _is_staff_manager(self):
        user = self.request.user
        return user.is_authenticated and user.role in ('admin', 'koordinator')

    def _is_petugas_lookup(self):
        user = self.request.user
        return user.is_authenticated and user.role == 'petugas'

    def get_serializer_class(self):
        if self.action == 'create':
            if self._is_staff_manager():
                return UserAdminSerializer
            return UserRegistrationSerializer
        if self._is_petugas_lookup() and self.action in ('list', 'retrieve'):
            return NasabahLookupSerializer
        if self.action in ('retrieve', 'update', 'partial_update'):
            if self.request.user.is_authenticated and self.request.user.role == 'nasabah':
                return UserProfileSerializer
            if self.request.user.is_authenticated and self.request.user.role == 'admin':
                return UserAdminSerializer
            return UserAdminSerializer
        return UserAdminSerializer

    def get_permissions(self):
        if self.action == 'create':
            if self._is_staff_manager():
                return [IsAdminOrKoordinator()]
            return [AllowAny()]
        if self.action == 'list':
            return [IsAuthenticated(), IsStaffManagerOrPetugas()]
        if self.action in ('retrieve', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsUserOwnerOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        if self._is_petugas_lookup():
            return qs.filter(role='nasabah', is_active=True)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        is_staff_create = self._is_staff_manager()
        return success_response(
            data=serializer.data,
            message=(
                'Pengguna berhasil dibuat.'
                if is_staff_create
                else 'Registrasi nasabah berhasil.'
            ),
            status_code=status.HTTP_201_CREATED,
            request=request,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message='Data berhasil diambil.',
            request=request,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(
            data=serializer.data,
            message='Data berhasil diperbarui.',
            request=request,
        )

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


@waste_category_schema
class KategoriSampahViewSet(viewsets.ModelViewSet):
    queryset = KategoriSampah.objects.all()
    serializer_class = KategoriSampahSerializer
    ordering_fields = ['nama', 'harga_beli_per_kg', 'stok_terkini_kg']
    ordering = ['nama']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        if self.action == 'destroy':
            return [IsAdmin()]
        return [IsAdminOrKoordinator()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(
            data=serializer.data,
            message='Kategori sampah berhasil dibuat.',
            status_code=status.HTTP_201_CREATED,
            request=request,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message='Data berhasil diambil.',
            request=request,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(
            data=serializer.data,
            message='Kategori sampah berhasil diperbarui.',
            request=request,
        )

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

@deposit_schema
class TransaksiSetoranViewSet(viewsets.ModelViewSet):
    queryset = TransaksiSetoran.objects.select_related(
        'nasabah', 'petugas',
    ).prefetch_related('details__kategori')
    filterset_class = TransaksiSetoranFilter
    ordering_fields = ['tanggal', 'total_nilai']
    ordering = ['-tanggal']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'create':
            return TransaksiSetoranCreateSerializer
        return TransaksiSetoranReadSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsPetugasOrAdmin(), IsPemerintahReadOnly()]
        return [IsAuthenticated(), IsOwnerOrAdmin(), IsPemerintahReadOnly()]

    def get_queryset(self):
        return filter_nasabah_owned(super().get_queryset(), self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = TransaksiSetoranReadSerializer(
            serializer.instance, context={'request': request},
        )
        return success_response(
            data=output.data,
            message='Transaksi setoran berhasil dicatat.',
            status_code=status.HTTP_201_CREATED,
            request=request,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TransaksiSetoranReadSerializer(
            instance, context={'request': request},
        )
        return success_response(
            data=serializer.data,
            message='Bukti setoran berhasil diambil.',
            request=request,
        )

@pickup_schema
class PenjemputanViewSet(viewsets.ModelViewSet):
    queryset = Penjemputan.objects.select_related('nasabah', 'petugas')
    filterset_fields = ['nasabah', 'status', 'petugas']
    ordering_fields = ['jadwal']
    ordering = ['-jadwal']
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'create':
            return PenjemputanCreateSerializer
        if self.action in ('partial_update', 'update'):
            return PenjemputanUpdateSerializer
        return PenjemputanSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsNasabah(), IsPemerintahReadOnly()]
        if self.action in ('partial_update', 'update', 'update_status'):
            return [IsAuthenticated(), IsPickupManager(), IsPemerintahReadOnly()]
        if self.action in ('approve', 'reject', 'assign'):
            return [IsAuthenticated(), IsAdmin(), IsPemerintahReadOnly()]
        return [IsAuthenticated(), IsOwnerOrAdmin(), IsPemerintahReadOnly()]

    def get_queryset(self):
        return filter_pickup_queryset(super().get_queryset(), self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = PenjemputanSerializer(serializer.instance, context={'request': request})
        return success_response(
            data=output.data,
            message='Penjemputan berhasil diajukan.',
            status_code=status.HTTP_201_CREATED,
            request=request,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PenjemputanSerializer(instance, context={'request': request})
        return success_response(
            data=serializer.data,
            message='Data berhasil diambil.',
            request=request,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        output = PenjemputanSerializer(serializer.instance, context={'request': request})
        return success_response(
            data=output.data,
            message='Penjemputan berhasil diperbarui.',
            request=request,
        )

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def _pickup_response(self, instance, message, request):
        output = PenjemputanSerializer(instance, context={'request': request})
        return success_response(data=output.data, message=message, request=request)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        instance = self.get_object()
        approve_pickup(instance, request.user)
        return self._pickup_response(
            instance, 'Penjemputan berhasil disetujui.', request,
        )

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        instance = self.get_object()
        reject_pickup(instance, request.user)
        return self._pickup_response(
            instance, 'Penjemputan berhasil ditolak.', request,
        )

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        instance = self.get_object()
        serializer = PickupAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assign_pickup(instance, request.user, serializer.validated_data['petugas_id'])
        return self._pickup_response(
            instance, 'Petugas berhasil ditugaskan.', request,
        )

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        instance = self.get_object()
        serializer = PickupStatusActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_pickup_status(
            instance, request.user, serializer.validated_data['status'],
        )
        return self._pickup_response(
            instance, 'Status penjemputan berhasil diperbarui.', request,
        )

@withdrawal_schema
class PenarikanSaldoViewSet(viewsets.ModelViewSet):
    queryset = PenarikanSaldo.objects.select_related('nasabah')
    filterset_fields = ['nasabah', 'status']
    ordering_fields = ['tanggal', 'nominal']
    ordering = ['-tanggal']
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'create':
            return PenarikanSaldoCreateSerializer
        if self.action in ('partial_update', 'update'):
            return PenarikanSaldoUpdateSerializer
        return PenarikanSaldoSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsNasabah(), IsPemerintahReadOnly()]
        if self.action in ('partial_update', 'update', 'approve', 'reject'):
            return [IsAuthenticated(), IsAdminOrKoordinator(), IsPemerintahReadOnly()]
        return [IsAuthenticated(), IsOwnerOrAdmin(), IsPemerintahReadOnly()]

    def get_queryset(self):
        return filter_nasabah_owned(super().get_queryset(), self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = PenarikanSaldoSerializer(serializer.instance, context={'request': request})
        return success_response(
            data=output.data,
            message='Penarikan saldo berhasil diajukan.',
            status_code=status.HTTP_201_CREATED,
            request=request,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PenarikanSaldoSerializer(instance, context={'request': request})
        return success_response(
            data=serializer.data,
            message='Data berhasil diambil.',
            request=request,
        )

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if old_status != 'selesai' and instance.status == 'selesai':
            debit_nasabah_saldo(instance.nasabah, instance.nominal)

        output = PenarikanSaldoSerializer(instance, context={'request': request})
        return success_response(
            data=output.data,
            message='Penarikan saldo berhasil disetujui.',
            request=request,
        )

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def _withdrawal_response(self, instance, message, request):
        output = PenarikanSaldoSerializer(instance, context={'request': request})
        return success_response(data=output.data, message=message, request=request)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        instance = self.get_object()
        approve_withdrawal(instance)
        debit_nasabah_saldo(instance.nasabah, instance.nominal)
        return self._withdrawal_response(
            instance, 'Penarikan saldo berhasil disetujui.', request,
        )

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        instance = self.get_object()
        reject_withdrawal(instance)
        return self._withdrawal_response(
            instance, 'Penarikan saldo berhasil ditolak.', request,
        )

@reward_schema
class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    ordering_fields = ['nama', 'poin_dibutuhkan', 'stok']
    ordering = ['nama']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin(), IsPemerintahReadOnly()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(
            data=serializer.data,
            message='Reward berhasil dibuat.',
            status_code=status.HTTP_201_CREATED,
            request=request,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message='Data berhasil diambil.',
            request=request,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(
            data=serializer.data,
            message='Reward berhasil diperbarui.',
            request=request,
        )

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

@redemption_schema
class PenukaranPoinViewSet(viewsets.ModelViewSet):
    queryset = PenukaranPoin.objects.select_related('nasabah', 'reward')
    filterset_fields = ['nasabah', 'status']
    ordering_fields = ['tanggal']
    ordering = ['-tanggal']
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'create':
            return PenukaranPoinCreateSerializer
        if self.action in ('partial_update', 'update'):
            return PenukaranPoinUpdateSerializer
        return PenukaranPoinSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsNasabah(), IsPemerintahReadOnly()]
        if self.action in ('partial_update', 'update', 'approve'):
            return [IsAuthenticated(), IsAdmin(), IsPemerintahReadOnly()]
        return [IsAuthenticated(), IsOwnerOrAdmin(), IsPemerintahReadOnly()]

    def get_queryset(self):
        return filter_nasabah_owned(super().get_queryset(), self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = PenukaranPoinSerializer(serializer.instance, context={'request': request})
        return success_response(
            data=output.data,
            message='Penukaran poin berhasil diajukan.',
            status_code=status.HTTP_201_CREATED,
            request=request,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PenukaranPoinSerializer(instance, context={'request': request})
        return success_response(
            data=serializer.data,
            message='Data berhasil diambil.',
            request=request,
        )

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if old_status != 'selesai' and instance.status == 'selesai':
            complete_penukaran_poin(instance.nasabah, instance.reward)

        output = PenukaranPoinSerializer(instance, context={'request': request})
        return success_response(
            data=output.data,
            message='Penukaran poin berhasil disetujui.',
            request=request,
        )

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        instance = self.get_object()
        approve_redemption(instance)
        complete_penukaran_poin(instance.nasabah, instance.reward)
        output = PenukaranPoinSerializer(instance, context={'request': request})
        return success_response(
            data=output.data,
            message='Penukaran poin berhasil disetujui.',
            request=request,
        )

@partner_schema
class MitraPengepulViewSet(viewsets.ModelViewSet):
    queryset = MitraPengepul.objects.all()
    serializer_class = MitraPengepulSerializer
    search_fields = ['nama', 'kontak']
    ordering_fields = ['nama']
    ordering = ['nama']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsMonitorReadOnly()]
        return [IsAuthenticated(), IsAdminOrKoordinator(), IsPemerintahReadOnly()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(
            data=serializer.data,
            message='Mitra pengepul berhasil dibuat.',
            status_code=status.HTTP_201_CREATED,
            request=request,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message='Data berhasil diambil.',
            request=request,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(
            data=serializer.data,
            message='Mitra pengepul berhasil diperbarui.',
            request=request,
        )

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

@partner_sale_schema
class PenjualanMitraViewSet(viewsets.ModelViewSet):
    queryset = PenjualanMitra.objects.select_related('mitra', 'kategori')
    filterset_fields = ['mitra', 'kategori']
    ordering_fields = ['tanggal', 'total_penjualan']
    ordering = ['-tanggal']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'create':
            return PenjualanMitraCreateSerializer
        return PenjualanMitraSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsMonitorReadOnly()]
        return [IsAuthenticated(), IsAdminOrKoordinator(), IsPemerintahReadOnly()]

    def get_queryset(self):
        return filter_staff_only(super().get_queryset(), self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = PenjualanMitraSerializer(serializer.instance, context={'request': request})
        return success_response(
            data=output.data,
            message='Penjualan ke mitra berhasil dicatat.',
            status_code=status.HTTP_201_CREATED,
            request=request,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PenjualanMitraSerializer(instance, context={'request': request})
        return success_response(
            data=serializer.data,
            message='Data berhasil diambil.',
            request=request,
        )

@complaint_schema
class PengaduanViewSet(viewsets.ModelViewSet):
    queryset = Pengaduan.objects.select_related('nasabah')
    filterset_fields = ['nasabah', 'status', 'jenis_pengaduan']
    ordering_fields = ['tanggal']
    ordering = ['-tanggal']
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'create':
            return PengaduanCreateSerializer
        if self.action in ('partial_update', 'update'):
            return PengaduanUpdateSerializer
        return PengaduanSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsNasabah(), IsPemerintahReadOnly()]
        if self.action in ('partial_update', 'update'):
            return [IsAuthenticated(), IsAdmin(), IsPemerintahReadOnly()]
        return [IsAuthenticated(), IsOwnerOrAdmin(), IsPemerintahReadOnly()]

    def get_queryset(self):
        return filter_nasabah_owned(super().get_queryset(), self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = PengaduanSerializer(serializer.instance, context={'request': request})
        return success_response(
            data=output.data,
            message='Pengaduan berhasil dibuat.',
            status_code=status.HTTP_201_CREATED,
            request=request,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PengaduanSerializer(instance, context={'request': request})
        return success_response(
            data=serializer.data,
            message='Data berhasil diambil.',
            request=request,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        output = PengaduanSerializer(serializer.instance, context={'request': request})
        return success_response(
            data=output.data,
            message='Pengaduan berhasil diperbarui.',
            request=request,
        )

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


@extend_schema(
    tags=[ACTIVITY_TAG],
    summary='Riwayat transaksi gabungan (setoran, penarikan, penukaran poin)',
    parameters=[
        {
            'name': 'jenis',
            'in': 'query',
            'required': False,
            'schema': {'type': 'string', 'enum': ['setoran', 'penarikan', 'poin']},
        },
        {
            'name': 'ordering',
            'in': 'query',
            'required': False,
            'schema': {'type': 'string', 'enum': ['tanggal', '-tanggal']},
        },
        {
            'name': 'nasabah',
            'in': 'query',
            'required': False,
            'schema': {'type': 'integer'},
            'description': 'Filter nasabah (staff only)',
        },
    ],
)
class ActivityListView(APIView):
    permission_classes = [IsAuthenticated, IsActivityReader, IsPemerintahReadOnly]

    def get(self, request):
        items = get_activity_items(
            request.user,
            jenis=request.query_params.get('jenis'),
            nasabah_id=request.query_params.get('nasabah'),
            ordering=request.query_params.get('ordering', '-tanggal'),
        )
        paginator = MiruPagination()
        page = paginator.paginate_queryset(items, request)
        return paginator.get_paginated_response(page)
