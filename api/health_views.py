from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .openapi import health_schema
from .utils.response import success_response


@health_schema
class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        db_status = 'connected'
        try:
            connection.ensure_connection()
        except Exception:
            db_status = 'disconnected'

        return success_response(
            data={
                'status': 'ok',
                'database': db_status,
            },
            message='Server berjalan normal.',
            request=request,
        )
