from django.apps import AppConfig


class ShowcaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'showcase'
    verbose_name = 'Vitrin'

    def ready(self):
        import showcase.signals  # noqa: F401
