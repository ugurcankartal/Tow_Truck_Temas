from django.contrib import admin
from django.utils.html import format_html

from .models import SiteVisit


@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = (
        'visited_at',
        'ip_address',
        'country',
        'city',
        'device_type',
        'browser',
        'os_name',
        'path',
        'is_bot',
    )
    list_filter = (
        'is_bot',
        'device_type',
        'country',
        'city',
        'browser',
        'os_name',
        ('visited_at', admin.DateFieldListFilter),
    )
    search_fields = (
        'ip_address',
        'city',
        'country',
        'region',
        'location_address',
        'user_agent',
        'path',
        'referrer',
        'visitor_key',
        'session_key',
    )
    readonly_fields = (
        'ip_address',
        'country',
        'country_code',
        'region',
        'city',
        'postal_code',
        'location_address',
        'latitude',
        'longitude',
        'timezone',
        'isp',
        'host',
        'path',
        'full_url',
        'referrer',
        'http_method',
        'accept_language',
        'user_agent',
        'device_type',
        'device_brand',
        'device_model',
        'browser',
        'browser_version',
        'os_name',
        'os_version',
        'is_bot',
        'screen_width',
        'screen_height',
        'viewport_width',
        'viewport_height',
        'session_key',
        'visitor_key',
        'visited_at',
        'map_link',
    )
    date_hierarchy = 'visited_at'
    ordering = ('-visited_at',)

    fieldsets = (
        ('Ziyaret', {
            'fields': (
                'visited_at',
                'path',
                'full_url',
                'referrer',
                'http_method',
                'host',
            ),
        }),
        ('Ağ & konum', {
            'fields': (
                'ip_address',
                'country',
                'country_code',
                'region',
                'city',
                'postal_code',
                'location_address',
                'latitude',
                'longitude',
                'timezone',
                'isp',
                'map_link',
            ),
        }),
        ('Cihaz', {
            'fields': (
                'device_type',
                'device_brand',
                'device_model',
                'browser',
                'browser_version',
                'os_name',
                'os_version',
                'is_bot',
                'screen_width',
                'screen_height',
                'viewport_width',
                'viewport_height',
                'accept_language',
                'user_agent',
            ),
        }),
        ('Oturum', {
            'fields': ('session_key', 'visitor_key'),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='Harita')
    def map_link(self, obj: SiteVisit):
        if obj.latitude is None or obj.longitude is None:
            return '—'
        url = (
            f'https://www.openstreetmap.org/?mlat={obj.latitude}'
            f'&mlon={obj.longitude}#map=12/{obj.latitude}/{obj.longitude}'
        )
        return format_html('<a href="{}" target="_blank" rel="noopener">Haritada aç</a>', url)
