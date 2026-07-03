from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Site Yönetimi'

    def ready(self):
        import core.signals  # noqa: F401
        import core.login_security_admin  # noqa: F401
        from core.admin_site import patch_admin_site
        from core.auth_admin import register_restricted_auth_admin

        register_restricted_auth_admin()
        patch_admin_site()
