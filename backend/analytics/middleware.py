from __future__ import annotations

import logging

from django.conf import settings

from analytics.services.capture import record_site_visit

logger = logging.getLogger(__name__)


class VisitorTrackingMiddleware:
    """Admin panel GET isteklerini arka planda SiteVisit olarak kaydeder."""

    SKIP_PREFIXES = (
        '/static/',
        '/media/',
        '/api/v1/analytics/visit/',
    )

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'VISITOR_TRACKING_MIDDLEWARE', True)

    def __call__(self, request):
        should_track = self.enabled and self._should_track(request)
        response = self.get_response(request)

        if should_track:
            try:
                record_site_visit(request, resolve_geo=True, background=True)
            except Exception:
                logger.exception('Admin visit tracking failed for %s', request.path)

        return response

    def _should_track(self, request) -> bool:
        if request.method != 'GET':
            return False

        path = request.path
        if not path.startswith('/admin/'):
            return False

        return not any(path.startswith(prefix) for prefix in self.SKIP_PREFIXES)
