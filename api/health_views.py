from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .utils.response import success_response


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return success_response(
            data={'status': 'ok'},
            message='Server berjalan normal.',
            request=request,
        )
