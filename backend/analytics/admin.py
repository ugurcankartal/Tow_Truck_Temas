from datetime import timedelta

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import SiteVisit

STAFF_USER_POPUP = "width=1100,height=800,resizable=yes,scrollbars=yes"


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
        'staff_user_display',
        'ip_address',
        'country',
        'city',
        'device_type',
        'browser',
        'os_name',
        'path',
        'is_bot',
    )
    list_display_links = ('staff_user_display', 'visited_at')
    list_filter = (
        VisitedAtFilter,
        'visit_source',
        'is_staff_session',
        'is_bot',
        'device_type',
        'country',
    )
    search_fields = (
        'staff_username',
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
        'staff_username_link',
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
                'staff_username_link',
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

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def _resolve_staff_user_id(self, obj: SiteVisit) -> int | None:
        if obj.staff_user_id:
            return obj.staff_user_id
        if not obj.staff_username:
            return None
        return (
            get_user_model().objects.filter(username=obj.staff_username)
            .values_list('pk', flat=True)
            .first()
        )

    def _staff_user_label(self, obj: SiteVisit) -> str:
        if obj.staff_username:
            return obj.staff_username
        if obj.visit_source == SiteVisit.VisitSource.ADMIN:
            return 'Anonim'
        return '—'

    @admin.display(description='Staff kullanıcı')
    def staff_user_display(self, obj: SiteVisit):
        return self._staff_user_label(obj)

    @admin.display(description='Staff kullanıcı')
    def staff_username_link(self, obj: SiteVisit):
        label = self._staff_user_label(obj)
        if label in ('—', 'Anonim'):
            return label

        user_id = self._resolve_staff_user_id(obj)
        if not user_id:
            return label

        url = reverse('admin:auth_user_change', args=[user_id])
        return format_html(
            '<a href="{}" onclick="window.open(this.href, \'staffUserPopup_{}\', '
            '\'{}\'); return false;">{}</a>',
            url,
            user_id,
            STAFF_USER_POPUP,
            label,
        )

    @admin.display(description='Harita')
    def map_link(self, obj: SiteVisit):
        if obj is None or obj.latitude is None or obj.longitude is None:
            return '—'
        url = (
            f'https://www.openstreetmap.org/?mlat={obj.latitude}'
            f'&mlon={obj.longitude}#map=12/{obj.latitude}/{obj.longitude}'
        )
        return format_html('<a href="{}" target="_blank" rel="noopener">Haritada aç</a>', url)
