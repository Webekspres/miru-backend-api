from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny

from .models import *
from .openapi import (
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
from .permissions import IsAdmin, IsAdminOrKoordinator, IsOwnerOrAdmin, IsUserOwnerOrAdmin
from .serializers import *
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

    def get_serializer_class(self):
        if self.action == 'create':
            if self._is_staff_manager():
                return UserAdminSerializer
            return UserRegistrationSerializer
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
        if self.action in ('retrieve', 'update', 'partial_update', 'destroy'):
            return [IsUserOwnerOrAdmin()]
        return super().get_permissions()

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
    queryset = TransaksiSetoran.objects.all()
    serializer_class = TransaksiSetoranSerializer
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ['nasabah', 'status']
    ordering_fields = ['tanggal', 'total_nilai']
    ordering = ['-tanggal']

@pickup_schema
class PenjemputanViewSet(viewsets.ModelViewSet):
    queryset = Penjemputan.objects.all()
    serializer_class = PenjemputanSerializer
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ['nasabah', 'status', 'petugas']
    ordering_fields = ['jadwal']
    ordering = ['-jadwal']

@withdrawal_schema
class PenarikanSaldoViewSet(viewsets.ModelViewSet):
    queryset = PenarikanSaldo.objects.all()
    serializer_class = PenarikanSaldoSerializer
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ['nasabah', 'status']
    ordering_fields = ['tanggal', 'nominal']
    ordering = ['-tanggal']
    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'selesai':
            nasabah = instance.nasabah
            nasabah.saldo -= instance.nominal
            nasabah.save()

@reward_schema
class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    ordering_fields = ['nama', 'poin_dibutuhkan']
    ordering = ['nama']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminOrKoordinator()]

@redemption_schema
class PenukaranPoinViewSet(viewsets.ModelViewSet):
    queryset = PenukaranPoin.objects.all()
    serializer_class = PenukaranPoinSerializer
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ['nasabah', 'status']
    ordering_fields = ['tanggal']
    ordering = ['-tanggal']
    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'selesai':
            nasabah = instance.nasabah
            nasabah.poin -= instance.reward.poin_dibutuhkan
            nasabah.save()

@partner_schema
class MitraPengepulViewSet(viewsets.ModelViewSet):
    queryset = MitraPengepul.objects.all()
    serializer_class = MitraPengepulSerializer
    permission_classes = [IsAdminOrKoordinator]
    search_fields = ['nama', 'kontak']
    ordering_fields = ['nama']
    ordering = ['nama']

@partner_sale_schema
class PenjualanMitraViewSet(viewsets.ModelViewSet):
    queryset = PenjualanMitra.objects.all()
    serializer_class = PenjualanMitraSerializer
    permission_classes = [IsAdminOrKoordinator]
    filterset_fields = ['mitra', 'kategori']
    ordering_fields = ['tanggal', 'total_penjualan']
    ordering = ['-tanggal']
    def perform_create(self, serializer):
        instance = serializer.save()
        kat = instance.kategori
        kat.stok_terkini_kg -= instance.berat_jual_kg
        kat.save()

@complaint_schema
class PengaduanViewSet(viewsets.ModelViewSet):
    queryset = Pengaduan.objects.all()
    serializer_class = PengaduanSerializer
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ['nasabah', 'status']
    ordering_fields = ['tanggal']
    ordering = ['-tanggal']
