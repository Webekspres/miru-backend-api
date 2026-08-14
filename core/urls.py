from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.shortcuts import redirect

from api.auth_views import MeView, MiruTokenObtainPairView, MiruTokenRefreshView
from api.flow_docs_views import FlowDocsView
from api.health_views import HealthCheckView
from api.media_views import PublicObjectView

urlpatterns = [
    path('', lambda r: redirect('/health/')),
    path('health/', HealthCheckView.as_view(), name='health'),
    path('api/auth/login/', MiruTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', MiruTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/me/', MeView.as_view(), name='auth_me'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/guide/', FlowDocsView.as_view(), name='flow-guide'),
    path('api/', include('api.urls')),
    path('objects/<path:key>', PublicObjectView.as_view(), name='public-object'),
]
