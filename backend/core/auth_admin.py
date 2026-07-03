from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class SupervisorHiddenUserAdmin(BaseUserAdmin):
    """Staff kullanıcı yönetimi açık; supervisor hesapları yalnızca supervisor'lara görünür."""

    def _is_supervisor(self, request) -> bool:
        return bool(request.user.is_active and request.user.is_superuser)

    def _is_hidden_supervisor(self, obj) -> bool:
        return bool(obj and obj.is_superuser)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not self._is_supervisor(request):
            qs = qs.filter(is_superuser=False)
        return qs

    def has_view_permission(self, request, obj=None):
        if obj is not None and self._is_hidden_supervisor(obj) and not self._is_supervisor(request):
            return False
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj is not None and self._is_hidden_supervisor(obj) and not self._is_supervisor(request):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and self._is_hidden_supervisor(obj) and not self._is_supervisor(request):
            return False
        return super().has_delete_permission(request, obj)

    def get_list_filter(self, request):
        if self._is_supervisor(request):
            return self.list_filter
        return ('is_staff', 'is_active')

    def get_fieldsets(self, request, obj=None):
        if self._is_supervisor(request):
            return super().get_fieldsets(request, obj)

        if obj is None:
            return self.add_fieldsets

        return (
            (None, {'fields': ('username', 'password')}),
            (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
            (_('Permissions'), {'fields': ('is_active', 'is_staff')}),
            (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )

    def save_model(self, request, obj, form, change):
        if not self._is_supervisor(request):
            obj.is_superuser = False
        super().save_model(request, obj, form, change)


def register_restricted_auth_admin() -> None:
    if User in admin.site._registry:
        admin.site.unregister(User)
    admin.site.register(User, SupervisorHiddenUserAdmin)
