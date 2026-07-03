from django.contrib import admin

LOGIN_SECURITY_MODELS = frozenset({
    'AdminLoginSecuritySettings',
    'AdminLoginUsernameLock',
    'AdminLoginDeviceLock',
    'AdminLoginFailedAttempt',
})
LOGIN_SECURITY_APP_LABEL = 'login_security'
LOGIN_SECURITY_APP_NAME = 'Giriş güvenliği'
LOGIN_SECURITY_APP_INDEX_URL_NAME = 'login_security_app_index'


def _login_security_app_url() -> str:
    from django.urls import reverse

    return reverse(f'admin:{LOGIN_SECURITY_APP_INDEX_URL_NAME}')


def _login_security_app_entry(security_models: list[dict]) -> dict:
    return {
        'name': LOGIN_SECURITY_APP_NAME,
        'app_label': LOGIN_SECURITY_APP_LABEL,
        'app_url': _login_security_app_url(),
        'has_module_perms': any(
            model_entry.get('perms', {}).get('view') for model_entry in security_models
        ),
        'models': security_models,
    }


def _split_login_security_app(app_list: list[dict]) -> list[dict]:
    security_models: list[dict] = []
    filtered: list[dict] = []

    for app in app_list:
        if app['app_label'] != 'core':
            filtered.append(app)
            continue

        core_models = []
        for model_entry in app['models']:
            if model_entry['object_name'] in LOGIN_SECURITY_MODELS:
                security_models.append(model_entry)
            else:
                core_models.append(model_entry)

        if core_models:
            filtered.append({**app, 'models': core_models})

    if security_models:
        filtered.append(_login_security_app_entry(security_models))

    return filtered


def _build_login_lockout_context(request) -> dict:
    from core.services.admin_login_rate_limit import check_admin_login_allowed, get_device_key

    username = request.POST.get('username', '')
    device_key, _, _ = get_device_key(request)
    status = check_admin_login_allowed(username, device_key)
    if status.allowed:
        return {}
    return {
        'login_lockout_active': True,
        'login_lockout_seconds': status.retry_after_seconds,
        'login_lockout_type': status.lock_type,
    }


def _patch_login_lockout(site) -> None:
    from django.contrib.auth.decorators import login_not_required
    from django.views.decorators.cache import never_cache

    original_login = site.login

    def login(request, extra_context=None):
        extra = dict(extra_context or {})
        extra.update(_build_login_lockout_context(request))
        return original_login(request, extra_context=extra)

    site.login = login_not_required(never_cache(login))


def _patch_login_security_urls(site) -> None:
    if getattr(site, '_login_security_urls_patched', False):
        return
    site._login_security_urls_patched = True

    original_get_urls = site.get_urls

    def get_urls():
        from django.urls import path

        urlpatterns = original_get_urls()

        def login_security_app_index(request):
            return site.app_index(request, LOGIN_SECURITY_APP_LABEL)

        insert_at = len(urlpatterns) - 1 if site.final_catch_all_view else len(urlpatterns)
        urlpatterns.insert(
            insert_at,
            path(
                f'{LOGIN_SECURITY_APP_LABEL}/',
                site.admin_view(login_security_app_index),
                name=LOGIN_SECURITY_APP_INDEX_URL_NAME,
            ),
        )
        return urlpatterns

    site.get_urls = get_urls


def patch_admin_site() -> None:
    site = admin.site
    from core.admin_login_form import RateLimitedAdminAuthenticationForm

    site.login_form = RateLimitedAdminAuthenticationForm
    site.login_template = 'admin/login_with_lockout.html'

    if not getattr(site, '_login_lockout_patched', False):
        _patch_login_lockout(site)
        site._login_lockout_patched = True

    _patch_login_security_urls(site)

    if getattr(site, '_branding_patched', False):
        return
    site._branding_patched = True

    original_each_context = site.each_context
    original_get_app_list = site.get_app_list

    def each_context(request):
        context = original_each_context(request)
        from core.admin_branding import get_admin_branding_name

        name = get_admin_branding_name()
        if name:
            context['site_header'] = name
            context['site_title'] = name
        return context

    def get_app_list(request, app_label=None):
        if app_label == LOGIN_SECURITY_APP_LABEL:
            app_list = _split_login_security_app(original_get_app_list(request))
            return [app for app in app_list if app['app_label'] == LOGIN_SECURITY_APP_LABEL]

        app_list = original_get_app_list(request, app_label)
        if app_label is not None:
            return app_list
        return _split_login_security_app(app_list)

    site.each_context = each_context
    site.get_app_list = get_app_list
