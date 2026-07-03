from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content'
    verbose_name = 'İçerik & Görseller'

    def ready(self):
        import content.signals  # noqa: F401
