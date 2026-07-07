from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'waste-categories', KategoriSampahViewSet, basename='waste-category')
router.register(r'deposits', TransaksiSetoranViewSet, basename='deposit')
router.register(r'pickups', PenjemputanViewSet, basename='pickup')
router.register(r'withdrawals', PenarikanSaldoViewSet, basename='withdrawal')
router.register(r'rewards', RewardViewSet, basename='reward')
router.register(r'reward-redemptions', PenukaranPoinViewSet, basename='reward-redemption')
router.register(r'partners', MitraPengepulViewSet, basename='partner')
router.register(r'partner-sales', PenjualanMitraViewSet, basename='partner-sale')
router.register(r'complaints', PengaduanViewSet, basename='complaint')

urlpatterns = [
    path('', include(router.urls)),
]
