from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'sampah/kategori', KategoriSampahViewSet, basename='kategori')
router.register(r'transaksi', TransaksiSetoranViewSet, basename='transaksi')
router.register(r'penjemputan', PenjemputanViewSet, basename='penjemputan')
router.register(r'saldo', PenarikanSaldoViewSet, basename='saldo')
router.register(r'reward/katalog', RewardViewSet, basename='reward')
router.register(r'reward/tukar', PenukaranPoinViewSet, basename='tukar')
router.register(r'gudang/mitra', MitraPengepulViewSet, basename='mitra')
router.register(r'gudang/jual', PenjualanMitraViewSet, basename='jual')
router.register(r'pengaduan', PengaduanViewSet, basename='pengaduan')

urlpatterns = [
    path('', include(router.urls)),
]
