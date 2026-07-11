from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.services.capture import record_site_visit

# 1x1 transparent GIF
TRACKING_PIXEL = (
    b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!'
    b'\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00'
    b'\x00\x02\x01D\x00;'
)


def _visit_extra_from_request(request) -> dict:
    source = request.data if isinstance(getattr(request, 'data', None), dict) else {}
    if source:
        return source

    query = getattr(request, 'query_params', None) or request.GET
    return {
        'path': query.get('path', ''),
        'full_url': query.get('full_url', ''),
        'referrer': query.get('referrer', ''),
        'screen_width': query.get('screen_width'),
        'screen_height': query.get('screen_height'),
        'viewport_width': query.get('viewport_width'),
        'viewport_height': query.get('viewport_height'),
    }


@method_decorator(csrf_exempt, name='dispatch')
class RecordVisitAPIView(APIView):
    """
    POST /api/v1/analytics/visit/

    Astro veya diğer istemcilerden ziyaret kaydı alır.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        visit = record_site_visit(request, extra=_visit_extra_from_request(request))
        return Response({'id': visit.pk, 'status': 'recorded'}, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class RecordVisitPixelView(APIView):
    """
    GET /api/v1/analytics/visit/pixel.gif

    Cloudflare/WAF uyumlu piksel takibi — img/beacon GET isteği.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        record_site_visit(
            request,
            extra=_visit_extra_from_request(request),
            background=True,
        )
        response = HttpResponse(TRACKING_PIXEL, content_type='image/gif')
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        return response
