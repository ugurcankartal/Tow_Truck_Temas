from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.services.admin_login_rate_limit import (
    check_admin_login_allowed,
    clear_admin_login_success,
    get_device_key,
    record_admin_login_failure,
)


class RateLimitedAdminAuthenticationForm(AdminAuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username', '')
        password = self.cleaned_data.get('password', '')
        device_key, ip_address, user_agent = get_device_key(self.request)

        status = check_admin_login_allowed(username, device_key)
        if not status.allowed:
            raise ValidationError(status.message)

        if username is not None and password:
            self.user_cache = self.authenticate(
                username=username,
                password=password,
            )
            if self.user_cache is None:
                record_admin_login_failure(
                    username,
                    device_key=device_key,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
                status = check_admin_login_allowed(username, device_key)
                if not status.allowed:
                    raise ValidationError(status.message)
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            self.confirm_login_allowed(self.user_cache)
            clear_admin_login_success(username, device_key)

        return self.cleaned_data

    def authenticate(self, username, password):
        from django.contrib.auth import authenticate

        return authenticate(self.request, username=username, password=password)
