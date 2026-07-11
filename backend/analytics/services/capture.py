from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any

from django.conf import settings

from analytics.models import SiteVisit
from analytics.services.device import parse_device_info
from analytics.services.geoip import lookup_geo
from analytics.services.request_meta import (
    build_visitor_key,
    get_accept_language,
    get_client_ip,
    header_value,
    is_public_ip,
)

logger = logging.getLogger(__name__)


@dataclass
class VisitCaptureData:
    ip_address: str
    user_agent: str
    session_key: str
    path: str
    full_url: str
    referrer: str
    http_method: str
    accept_language: str
    host: str
    screen_width: int | None = None
    screen_height: int | None = None
    viewport_width: int | None = None
    viewport_height: int | None = None


def _optional_int(value: Any) -> int | None:
    if value in (None, ''):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _optional_str(value: Any, max_length: int) -> str:
    if value is None:
        return ''
    return str(value).strip()[:max_length]


def _session_key(request, *, create: bool = False) -> str:
    if not hasattr(request, 'session'):
        return ''
    if create and not request.session.session_key:
        request.session.save()
    return ((request.session.session_key if hasattr(request, 'session') else '') or '')[:64]


def extract_visit_data(
    request,
    extra: dict | None = None,
    *,
    session_key: str | None = None,
) -> VisitCaptureData:
    extra = extra or {}
    ip_address = get_client_ip(request)
    user_agent = header_value(request, 'HTTP_USER_AGENT')
    path = _optional_str(extra.get('path') or request.path, 500)
    full_url = _optional_str(
        extra.get('full_url') or request.build_absolute_uri(path or '/'),
        2000,
    )
    referrer = _optional_str(
        extra.get('referrer') or header_value(request, 'HTTP_REFERER'),
        2000,
    )

    if session_key is None:
        session_key = _session_key(request, create=bool(extra.get('_create_session')))

    return VisitCaptureData(
        ip_address=ip_address,
        user_agent=user_agent[:5000],
        session_key=session_key,
        path=path,
        full_url=full_url,
        referrer=referrer,
        http_method=(request.method or 'GET')[:10],
        accept_language=get_accept_language(request),
        host=_optional_str(header_value(request, 'HTTP_HOST'), 255),
        screen_width=_optional_int(extra.get('screen_width')),
        screen_height=_optional_int(extra.get('screen_height')),
        viewport_width=_optional_int(extra.get('viewport_width')),
        viewport_height=_optional_int(extra.get('viewport_height')),
    )


def save_site_visit(data: VisitCaptureData, *, resolve_geo: bool = True) -> SiteVisit:
    device = parse_device_info(data.user_agent)
    geo = (
        lookup_geo(data.ip_address)
        if resolve_geo and is_public_ip(data.ip_address)
        else None
    )

    return SiteVisit.objects.create(
        ip_address=data.ip_address or None,
        country=geo.country if geo else '',
        country_code=geo.country_code if geo else '',
        region=geo.region if geo else '',
        city=geo.city if geo else '',
        postal_code=geo.postal_code if geo else '',
        location_address=geo.location_address if geo else '',
        latitude=geo.latitude if geo else None,
        longitude=geo.longitude if geo else None,
        timezone=geo.timezone if geo else '',
        isp=geo.isp if geo else '',
        host=data.host,
        path=data.path,
        full_url=data.full_url,
        referrer=data.referrer,
        http_method=data.http_method,
        accept_language=data.accept_language,
        user_agent=data.user_agent,
        device_type=device.device_type,
        device_brand=device.device_brand,
        device_model=device.device_model,
        browser=device.browser,
        browser_version=device.browser_version,
        os_name=device.os_name,
        os_version=device.os_version,
        is_bot=device.is_bot,
        screen_width=data.screen_width,
        screen_height=data.screen_height,
        viewport_width=data.viewport_width,
        viewport_height=data.viewport_height,
        session_key=data.session_key,
        visitor_key=build_visitor_key(
            data.ip_address,
            data.user_agent,
            data.session_key,
        )[:64],
    )


def record_site_visit(
    request,
    extra: dict | None = None,
    *,
    resolve_geo: bool = True,
    background: bool = False,
    session_key: str | None = None,
) -> SiteVisit | None:
    payload = dict(extra or {})
    if session_key is not None:
        payload.setdefault('_create_session', False)
    elif payload.get('_create_session') is None and not background:
        payload['_create_session'] = True

    data = extract_visit_data(request, payload, session_key=session_key)

    if background:
        thread = threading.Thread(
            target=save_site_visit,
            args=(data,),
            kwargs={'resolve_geo': resolve_geo},
            daemon=True,
        )
        thread.start()
        return None

    return save_site_visit(data, resolve_geo=resolve_geo)
