from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from .permissions import *

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrKoordinator]

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update'] and self.request.user.is_authenticated:
            return [IsOwnerOrAdmin()]
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

class KategoriSampahViewSet(viewsets.ModelViewSet):
    queryset = KategoriSampah.objects.all()
    serializer_class = KategoriSampahSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminOrKoordinator()]

class TransaksiSetoranViewSet(viewsets.ModelViewSet):
    queryset = TransaksiSetoran.objects.all()
    serializer_class = TransaksiSetoranSerializer
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ['nasabah']

class PenjemputanViewSet(viewsets.ModelViewSet):
    queryset = Penjemputan.objects.all()
    serializer_class = PenjemputanSerializer
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = ['nasabah', 'status']

class PenarikanSaldoViewSet(viewsets.ModelViewSet):
    queryset = PenarikanSaldo.objects.all()
    serializer_class = PenarikanSaldoSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'selesai':
            nasabah = instance.nasabah
            nasabah.saldo -= instance.nominal
            nasabah.save()

class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer

class PenukaranPoinViewSet(viewsets.ModelViewSet):
    queryset = PenukaranPoin.objects.all()
    serializer_class = PenukaranPoinSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'selesai':
            nasabah = instance.nasabah
            nasabah.poin -= instance.reward.poin_dibutuhkan
            nasabah.save()

class MitraPengepulViewSet(viewsets.ModelViewSet):
    queryset = MitraPengepul.objects.all()
    serializer_class = MitraPengepulSerializer
    permission_classes = [IsAdminOrKoordinator]

class PenjualanMitraViewSet(viewsets.ModelViewSet):
    queryset = PenjualanMitra.objects.all()
    serializer_class = PenjualanMitraSerializer
    permission_classes = [IsAdminOrKoordinator]

    def perform_create(self, serializer):
        instance = serializer.save()
        kat = instance.kategori
        kat.stok_terkini_kg -= instance.berat_jual_kg
        kat.save()

class PengaduanViewSet(viewsets.ModelViewSet):
    queryset = Pengaduan.objects.all()
    serializer_class = PengaduanSerializer
    permission_classes = [IsOwnerOrAdmin]
