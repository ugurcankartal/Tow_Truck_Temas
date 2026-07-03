from django.http import HttpResponse
from django.views.decorators.http import require_GET

from core.services.seo import (
    build_sitemap_entries,
    get_seo_context,
    render_robots_txt,
    render_sitemap_xml,
)


def _seo_cache_headers(response: HttpResponse) -> HttpResponse:
    response['Cache-Control'] = 'public, max-age=300, must-revalidate'
    response['X-Robots-Tag'] = 'noindex'
    response['X-Content-Type-Options'] = 'nosniff'
    return response


def _is_browser_request(request) -> bool:
    accept = request.META.get('HTTP_ACCEPT', '')
    return 'text/html' in accept and 'application/xml' not in accept.split(',')[0]


def _sitemap_response(content: str, *, browser_view: bool) -> HttpResponse:
    content_type = (
        'text/plain; charset=utf-8'
        if browser_view
        else 'application/xml; charset=utf-8'
    )
    response = HttpResponse(content, content_type=content_type)
    return _seo_cache_headers(response)


@require_GET
def robots_txt_view(request):
    base_url, indexable = get_seo_context(request)
    content = render_robots_txt(base_url, indexable=indexable)
    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    return _seo_cache_headers(response)


@require_GET
def sitemap_xml_view(request):
    base_url, indexable = get_seo_context(request)
    entries = build_sitemap_entries(base_url=base_url, indexable=indexable)
    content = render_sitemap_xml(base_url, entries)
    return _sitemap_response(content, browser_view=_is_browser_request(request))
