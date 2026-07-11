from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.services.capture import record_site_visit


@method_decorator(csrf_exempt, name='dispatch')
class RecordVisitAPIView(APIView):
    """
    POST /api/v1/analytics/visit/

    Astro veya diğer istemcilerden ziyaret kaydı alır.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        visit = record_site_visit(request, extra=request.data if isinstance(request.data, dict) else {})
        return Response({'id': visit.pk, 'status': 'recorded'}, status=status.HTTP_201_CREATED)
