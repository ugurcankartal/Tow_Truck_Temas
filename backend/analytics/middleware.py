from __future__ import annotations

import logging

from django.conf import settings

from analytics.models import SiteVisit
from analytics.services.capture import record_site_visit

logger = logging.getLogger(__name__)


class VisitorTrackingMiddleware:
    """Admin panel GET isteklerini anonim olarak kaydeder (superuser hariç)."""

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
        session_key = ''
        if should_track and hasattr(request, 'session'):
            session_key = request.session.session_key or ''

        response = self.get_response(request)

        if should_track:
            try:
                user = getattr(request, 'user', None)
                is_staff_session = bool(
                    user
                    and user.is_authenticated
                    and user.is_staff
                    and not user.is_superuser
                )
                staff_username = user.get_username() if is_staff_session else ''
                record_site_visit(
                    request,
                    extra={
                        'visit_source': SiteVisit.VisitSource.ADMIN,
                        'is_staff_session': is_staff_session,
                        'staff_username': staff_username,
                    },
                    resolve_geo=True,
                    background=True,
                    session_key=session_key,
                )
            except Exception:
                logger.exception('Admin visit tracking failed for %s', request.path)

        return response

    def _should_track(self, request) -> bool:
        if request.method != 'GET':
            return False

        path = request.path
        if not path.startswith('/admin/'):
            return False

        if any(path.startswith(prefix) for prefix in self.SKIP_PREFIXES):
            return False

        user = getattr(request, 'user', None)
        if user and user.is_authenticated and user.is_superuser:
            return False

        return True
