from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.conf import settings

logger = logging.getLogger(__name__)

GEO_FIELDS = (
    'status,message,country,countryCode,region,regionName,city,zip,lat,lon,'
    'timezone,isp,org,query'
)


@dataclass(frozen=True)
class GeoLocation:
    country: str = ''
    country_code: str = ''
    region: str = ''
    city: str = ''
    postal_code: str = ''
    latitude: str | None = None
    longitude: str | None = None
    timezone: str = ''
    isp: str = ''
    location_address: str = ''


def _build_location_address(city: str, region: str, country: str, postal_code: str) -> str:
    parts = [part for part in (city, region, postal_code, country) if part]
    return ', '.join(parts)


def lookup_geo(ip: str) -> GeoLocation:
    if not getattr(settings, 'VISITOR_GEO_LOOKUP', True):
        return GeoLocation()

    template = getattr(
        settings,
        'VISITOR_GEO_API_URL',
        'http://ip-api.com/json/{ip}?fields=' + GEO_FIELDS,
    )
    url = template.format(ip=ip)
    timeout = getattr(settings, 'VISITOR_GEO_TIMEOUT', 2)

    try:
        request = Request(url, headers={'User-Agent': 'TowTruckTemas-Analytics/1.0'})
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except (URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        logger.warning('GeoIP lookup failed for %s: %s', ip, exc)
        return GeoLocation()

    if payload.get('status') != 'success':
        return GeoLocation()

    city = (payload.get('city') or '')[:100]
    region = (payload.get('regionName') or '')[:100]
    country = (payload.get('country') or '')[:100]
    postal_code = (payload.get('zip') or '')[:20]

    lat = payload.get('lat')
    lon = payload.get('lon')

    return GeoLocation(
        country=country,
        country_code=(payload.get('countryCode') or '')[:2],
        region=region,
        city=city,
        postal_code=postal_code,
        latitude=str(lat) if lat is not None else None,
        longitude=str(lon) if lon is not None else None,
        timezone=(payload.get('timezone') or '')[:64],
        isp=(payload.get('isp') or payload.get('org') or '')[:255],
        location_address=_build_location_address(city, region, country, postal_code),
    )
