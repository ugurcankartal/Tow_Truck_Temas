from datetime import timedelta

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import SiteVisit


class VisitedAtFilter(admin.SimpleListFilter):
    title = 'Ziyaret zamanı'
    parameter_name = 'visited'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Bugün'),
            ('7d', 'Son 7 gün'),
            ('30d', 'Son 30 gün'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        value = self.value()
        if value == 'today':
            return queryset.filter(visited_at__gte=now.replace(hour=0, minute=0, second=0, microsecond=0))
        if value == '7d':
            return queryset.filter(visited_at__gte=now - timedelta(days=7))
        if value == '30d':
            return queryset.filter(visited_at__gte=now - timedelta(days=30))
        return queryset


@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = (
        'visited_at',
        'visit_source',
        'is_staff_session',
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
        VisitedAtFilter,
        'visit_source',
        'is_staff_session',
        'is_bot',
        'device_type',
        'country',
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
        'visit_source',
        'is_staff_session',
        'visited_at',
        'map_link',
    )
    ordering = ('-visited_at',)
    list_per_page = 50

    fieldsets = (
        ('Ziyaret', {
            'fields': (
                'visited_at',
                'visit_source',
                'is_staff_session',
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

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description='Harita')
    def map_link(self, obj: SiteVisit):
        if obj is None or obj.latitude is None or obj.longitude is None:
            return '—'
        url = (
            f'https://www.openstreetmap.org/?mlat={obj.latitude}'
            f'&mlon={obj.longitude}#map=12/{obj.latitude}/{obj.longitude}'
        )
        return format_html('<a href="{}" target="_blank" rel="noopener">Haritada aç</a>', url)
