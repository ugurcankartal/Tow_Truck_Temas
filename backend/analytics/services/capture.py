from __future__ import annotations

from typing import Any

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


def record_site_visit(request, extra: dict | None = None) -> SiteVisit:
    extra = extra or {}
    ip_address = get_client_ip(request)
    user_agent = header_value(request, 'HTTP_USER_AGENT')
    session_key = ''
    if hasattr(request, 'session') and request.session.session_key:
        session_key = request.session.session_key

    device = parse_device_info(user_agent)
    geo = lookup_geo(ip_address) if is_public_ip(ip_address) else None

    path = _optional_str(extra.get('path') or request.path, 500)
    full_url = _optional_str(
        extra.get('full_url') or request.build_absolute_uri(path or '/'),
        2000,
    )
    referrer = _optional_str(
        extra.get('referrer') or header_value(request, 'HTTP_REFERER'),
        2000,
    )

    visit = SiteVisit.objects.create(
        ip_address=ip_address or None,
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
        host=_optional_str(header_value(request, 'HTTP_HOST'), 255),
        path=path,
        full_url=full_url,
        referrer=referrer,
        http_method=(request.method or 'GET')[:10],
        accept_language=get_accept_language(request),
        user_agent=user_agent[:5000],
        device_type=device.device_type,
        device_brand=device.device_brand,
        device_model=device.device_model,
        browser=device.browser,
        browser_version=device.browser_version,
        os_name=device.os_name,
        os_version=device.os_version,
        is_bot=device.is_bot,
        screen_width=_optional_int(extra.get('screen_width')),
        screen_height=_optional_int(extra.get('screen_height')),
        viewport_width=_optional_int(extra.get('viewport_width')),
        viewport_height=_optional_int(extra.get('viewport_height')),
        session_key=session_key[:64],
        visitor_key=build_visitor_key(ip_address, user_agent, session_key)[:64],
    )
    return visit
