from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.shortcuts import redirect

from api.auth_views import MiruTokenObtainPairView, MiruTokenRefreshView
from api.health_views import HealthCheckView

urlpatterns = [
    path('', lambda r: redirect('/health/')),
    path('health/', HealthCheckView.as_view(), name='health'),
    path('api/auth/login/', MiruTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', MiruTokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include('api.urls')),
]
