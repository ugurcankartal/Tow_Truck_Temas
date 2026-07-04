"""SSG içeriğini etkileyen tüm modellerde kayıt/silme sonrası Astro rebuild."""

from django.apps import apps
from django.db.models.signals import post_delete, post_save

from core.services.astro_rebuild import trigger_astro_rebuild

# (app_label, model_name)
ASTRO_REBUILD_MODELS: tuple[tuple[str, str], ...] = (
    ('core', 'SiteSettings'),
    ('core', 'SiteSettingsTranslation'),
    ('core', 'FAQ'),
    ('core', 'FAQTranslation'),
    ('content', 'ContentZone'),
    ('content', 'ContentZoneTranslation'),
    ('content', 'SiteImage'),
    ('content', 'SiteImageTranslation'),
    ('content', 'SiteImagePlacement'),
    ('showcase', 'ShowcaseStat'),
    ('showcase', 'ShowcaseStatTranslation'),
    ('showcase', 'ShowcaseServiceSection'),
    ('showcase', 'ShowcaseServiceSectionTranslation'),
    ('showcase', 'ShowcaseService'),
    ('showcase', 'ShowcaseServiceTranslation'),
    ('localization', 'Language'),
    ('localization', 'UiString'),
)


def _rebuild_source(model, action: str) -> str:
    return f'{model._meta.label_lower}_{action}'


def _on_save(sender, instance, **kwargs):
    updated_at = None
    if getattr(instance, 'updated_at', None):
        updated_at = instance.updated_at.isoformat()
    trigger_astro_rebuild(
        source=_rebuild_source(sender, 'save'),
        updated_at=updated_at,
    )


def _on_delete(sender, instance, **kwargs):
    trigger_astro_rebuild(source=_rebuild_source(sender, 'delete'))


def connect_astro_rebuild_signals() -> None:
    for app_label, model_name in ASTRO_REBUILD_MODELS:
        model = apps.get_model(app_label, model_name)
        label = model._meta.label_lower
        post_save.connect(
            _on_save,
            sender=model,
            dispatch_uid=f'astro-rebuild-save-{label}',
        )
        post_delete.connect(
            _on_delete,
            sender=model,
            dispatch_uid=f'astro-rebuild-delete-{label}',
        )
