from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from xml.etree import ElementTree as ET

from django.conf import settings as django_settings
from django.utils import timezone

from localization.models import Language

SITEMAP_NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
XHTML_NS = 'http://www.w3.org/1999/xhtml'

ET.register_namespace('', SITEMAP_NS)
ET.register_namespace('xhtml', XHTML_NS)


@dataclass(frozen=True)
class SitemapEntry:
    path: str
    lastmod: datetime | None = None
    changefreq: str = 'weekly'
    priority: str = '0.5'
    hreflang_alternates: tuple[tuple[str, str], ...] = ()


def get_site_base_url(request=None) -> str:
    """Öncelik: SiteSettings.site_url → SITE_URL → istek hostu."""
    from core.models import SiteSettings

    try:
        row = SiteSettings.objects.only('site_url').first()
        if row and row.site_url:
            return row.site_url.rstrip('/')
    except Exception:
        pass

    configured = (
        os.environ.get('SITE_URL', '').strip()
        or getattr(django_settings, 'SITE_URL', '').strip()
    )
    if configured:
        return configured.rstrip('/')

    if request is not None:
        scheme = 'https' if request.is_secure() else 'http'
        forwarded_proto = request.META.get('HTTP_X_FORWARDED_PROTO', '').split(',')[0].strip()
        if forwarded_proto in {'http', 'https'}:
            scheme = forwarded_proto
        return f'{scheme}://{request.get_host()}'.rstrip('/')

    return 'http://localhost:4321'


def is_site_indexable(robots: str) -> bool:
    normalized = robots.lower().replace(' ', '')
    return 'noindex' not in normalized


def _format_lastmod(value: datetime | None) -> str:
    if value is None:
        return timezone.localdate().isoformat()
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    return timezone.localtime(value).date().isoformat()


def _locale_path(code: str, default_code: str) -> str:
    if code == default_code:
        return '/'
    return f'/{code}/'


def _active_languages() -> tuple[Language, ...]:
    return tuple(Language.objects.filter(is_active=True).order_by('sort_order', 'code'))


def _default_language_code(languages: tuple[Language, ...]) -> str:
    for lang in languages:
        if lang.is_default:
            return lang.code
    for lang in languages:
        if lang.code == 'tr':
            return lang.code
    if languages:
        return languages[0].code
    return 'tr'


def _hreflang_alternates(
    base_url: str,
    languages: tuple[Language, ...],
    default_code: str,
) -> tuple[tuple[str, str], ...]:
    pairs: list[tuple[str, str]] = []
    default_href = base_url + '/'

    for lang in languages:
        href = f'{base_url}{_locale_path(lang.code, default_code)}'
        pairs.append((lang.code, href))
        if lang.code == default_code:
            default_href = href

    pairs.append(('x-default', default_href))
    return tuple(pairs)


def build_sitemap_entries(*, base_url: str, indexable: bool) -> list[SitemapEntry]:
    if not indexable:
        return []

    from core.models import SiteSettings

    settings_row = SiteSettings.objects.only('updated_at', 'robots').first()
    lastmod = settings_row.updated_at if settings_row else None

    languages = _active_languages()
    if not languages:
        languages = (Language(code='tr', name_native='Türkçe', is_default=True),)

    default_code = _default_language_code(languages)
    alternates = _hreflang_alternates(base_url, languages, default_code)

    entries: list[SitemapEntry] = []
    for lang in languages:
        path = _locale_path(lang.code, default_code)
        entries.append(
            SitemapEntry(
                path=path,
                lastmod=lastmod,
                changefreq='weekly',
                priority='1.0' if path == '/' else '0.9',
                hreflang_alternates=alternates,
            ),
        )
    return entries


def render_robots_txt(base_url: str, *, indexable: bool) -> str:
    sitemap_url = f'{base_url}/sitemap.xml'
    lines = ['User-agent: *']

    if indexable:
        lines.extend([
            'Allow: /',
            'Disallow: /admin/',
            'Disallow: /api/',
        ])
    else:
        lines.append('Disallow: /')

    lines.append('')
    lines.append(f'Sitemap: {sitemap_url}')
    return '\n'.join(lines) + '\n'


def render_sitemap_xml(base_url: str, entries: list[SitemapEntry]) -> str:
    urlset = ET.Element(f'{{{SITEMAP_NS}}}urlset')

    for entry in entries:
        url_elem = ET.SubElement(urlset, f'{{{SITEMAP_NS}}}url')

        loc = ET.SubElement(url_elem, f'{{{SITEMAP_NS}}}loc')
        loc.text = f'{base_url}{entry.path}'

        for hreflang, href in entry.hreflang_alternates:
            link = ET.SubElement(url_elem, f'{{{XHTML_NS}}}link')
            link.set('rel', 'alternate')
            link.set('hreflang', hreflang)
            link.set('href', href)

        lastmod = ET.SubElement(url_elem, f'{{{SITEMAP_NS}}}lastmod')
        lastmod.text = _format_lastmod(entry.lastmod)

        changefreq = ET.SubElement(url_elem, f'{{{SITEMAP_NS}}}changefreq')
        changefreq.text = entry.changefreq

        priority = ET.SubElement(url_elem, f'{{{SITEMAP_NS}}}priority')
        priority.text = entry.priority

    ET.indent(urlset, space='  ')
    buffer = BytesIO()
    ET.ElementTree(urlset).write(
        buffer,
        encoding='UTF-8',
        xml_declaration=True,
        short_empty_elements=False,
    )
    raw = buffer.getvalue().decode('utf-8')
    return raw.replace(
        "<?xml version='1.0' encoding='UTF-8'?>",
        '<?xml version="1.0" encoding="UTF-8"?>',
        1,
    )


def get_seo_context(request=None) -> tuple[str, bool]:
    """(base_url, indexable) döner."""
    from core.models import SiteSettings

    base_url = get_site_base_url(request)
    robots = 'index, follow'
    try:
        row = SiteSettings.objects.only('robots').first()
        if row and row.robots:
            robots = row.robots
    except Exception:
        pass
    return base_url, is_site_indexable(robots)
