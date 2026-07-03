from django.contrib import admin, messages
from django.utils.html import format_html

from core.login_security_models import (
    AdminLoginDeviceLock,
    AdminLoginFailedAttempt,
    AdminLoginSecuritySettings,
    AdminLoginUsernameLock,
)
from core.services.admin_login_rate_limit import reset_device_lock, reset_username_lock


def _is_supervisor(request) -> bool:
    return bool(request.user.is_active and request.user.is_superuser)


class SupervisorOnlyAdminMixin:
    def has_module_permission(self, request):
        return _is_supervisor(request)

    def has_view_permission(self, request, obj=None):
        return _is_supervisor(request)

    def has_add_permission(self, request):
        return _is_supervisor(request)

    def has_change_permission(self, request, obj=None):
        return _is_supervisor(request)

    def has_delete_permission(self, request, obj=None):
        return _is_supervisor(request)


@admin.register(AdminLoginSecuritySettings)
class AdminLoginSecuritySettingsAdmin(SupervisorOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('__str__', 'window_minutes', 'max_attempts', 'lockout_minutes', 'updated_at')
    fields = ('window_minutes', 'max_attempts', 'lockout_minutes', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        if AdminLoginSecuritySettings.objects.exists():
            return False
        return _is_supervisor(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        AdminLoginSecuritySettings.load()
        return super().changelist_view(request, extra_context)


@admin.action(description='Cezayı sıfırla')
def reset_username_lock_action(modeladmin, request, queryset):
    count = 0
    for lock in queryset:
        reset_username_lock(lock.username)
        count += 1
    modeladmin.message_user(request, f'{count} kullanıcı adı cezası sıfırlandı.', messages.SUCCESS)


@admin.register(AdminLoginUsernameLock)
class AdminLoginUsernameLockAdmin(SupervisorOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('username', 'locked_until', 'is_active_display', 'updated_at')
    search_fields = ('username',)
    readonly_fields = ('username', 'locked_until', 'created_at', 'updated_at')
    actions = [reset_username_lock_action]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='Aktif', boolean=True)
    def is_active_display(self, obj):
        from django.utils import timezone

        return obj.locked_until > timezone.now()


@admin.action(description='Cezayı sıfırla')
def reset_device_lock_action(modeladmin, request, queryset):
    count = 0
    for lock in queryset:
        reset_device_lock(lock.device_key)
        count += 1
    modeladmin.message_user(request, f'{count} cihaz cezası sıfırlandı.', messages.SUCCESS)


@admin.register(AdminLoginDeviceLock)
class AdminLoginDeviceLockAdmin(SupervisorOnlyAdminMixin, admin.ModelAdmin):
    list_display = (
        'device_key_short',
        'ip_address',
        'user_agent_short',
        'locked_until',
        'is_active_display',
        'updated_at',
    )
    search_fields = ('device_key', 'ip_address', 'user_agent')
    readonly_fields = (
        'device_key',
        'ip_address',
        'user_agent',
        'locked_until',
        'created_at',
        'updated_at',
    )
    actions = [reset_device_lock_action]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='Cihaz')
    def device_key_short(self, obj):
        return format_html('<code>{}…</code>', obj.device_key[:12])

    @admin.display(description='User-Agent')
    def user_agent_short(self, obj):
        if not obj.user_agent:
            return '—'
        return obj.user_agent[:60] + ('…' if len(obj.user_agent) > 60 else '')

    @admin.display(description='Aktif', boolean=True)
    def is_active_display(self, obj):
        from django.utils import timezone

        return obj.locked_until > timezone.now()


@admin.register(AdminLoginFailedAttempt)
class AdminLoginFailedAttemptAdmin(SupervisorOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('created_at', 'username', 'ip_address', 'device_key_short')
    search_fields = ('username', 'ip_address', 'device_key')
    readonly_fields = [f.name for f in AdminLoginFailedAttempt._meta.fields]
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='Cihaz')
    def device_key_short(self, obj):
        return format_html('<code>{}…</code>', obj.device_key[:12])
