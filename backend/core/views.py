from django.conf import settings as django_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .i18n import localized_text, resolve_request_language
from .models import ContactMessage, SiteSettings
from .serializers import ContactMessageSerializer, SiteSettingsSerializer
from .services.astro_rebuild import trigger_astro_rebuild


class APIRootView(APIView):
    """GET /api/v1/ — kullanılabilir uç noktalar."""

    def get(self, request):
        return Response({
            'version': 'v1',
            'endpoints': {
                'site_settings': request.build_absolute_uri(
                    reverse('site-settings'),
                ),
                'contact': request.build_absolute_uri(reverse('contact')),
                'languages': request.build_absolute_uri(reverse('languages')),
                'i18n_bundle': request.build_absolute_uri(reverse('i18n-bundle')),
                'robots_txt': request.build_absolute_uri(reverse('api-robots-txt')),
                'sitemap_xml': request.build_absolute_uri(reverse('api-sitemap-xml')),
            },
        })


class SiteSettingsAPIView(APIView):
    """
    GET /api/v1/site-settings/

    Astro build-time fetch için tekil site ayarları.
    SEO meta, NAP, SSS ve JSON-LD tek yanıtta döner.
    """

    def get(self, request):
        lang = resolve_request_language(request)
        settings = SiteSettings.objects.prefetch_related('translations__language').get(pk=1)
        serializer = SiteSettingsSerializer(
            settings,
            context={'request': request, 'language_code': lang},
        )
        data = serializer.data
        data['language'] = lang
        response = Response(data)
        response['Last-Modified'] = settings.updated_at.strftime(
            '%a, %d %b %Y %H:%M:%S GMT'
        )
        return response


class ContactAPIView(APIView):
    """
    POST /api/v1/contact/

    İletişim formu — Astro frontend'den JSON gönderilir.
    """

    def post(self, request):
        lang = resolve_request_language(request)
        serializer = ContactMessageSerializer(
            data=request.data,
            context={'language_code': lang},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': localized_text('contact_success', lang)},
            status=status.HTTP_201_CREATED,
        )


class TriggerRebuildAPIView(APIView):
    """
    POST /api/v1/trigger-rebuild/

    Manuel veya CI tarafından Astro rebuild tetiklemek için.
    Header: X-Webhook-Secret: <ASTRO_REBUILD_WEBHOOK_SECRET>
    """

    def post(self, request):
        secret = django_settings.ASTRO_REBUILD_WEBHOOK_SECRET
        if not secret:
            return Response(
                {'detail': 'Webhook secret yapılandırılmamış.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if request.headers.get('X-Webhook-Secret') != secret:
            return Response({'detail': 'Yetkisiz.'}, status=status.HTTP_403_FORBIDDEN)

        source = request.data.get('source', 'manual_api') if hasattr(request, 'data') else 'manual_api'
        trigger_astro_rebuild(source=source, async_run=False)

        return Response({'detail': 'Astro rebuild tetiklendi.', 'source': source})
