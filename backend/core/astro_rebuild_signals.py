"""SSG içeriğini etkileyen tüm modellerde kayıt/silme sonrası Astro rebuild."""

import logging

from django.apps import apps
from django.db.models.signals import post_delete, post_save

from core.services.astro_rebuild import trigger_astro_rebuild

logger = logging.getLogger(__name__)

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
    source = _rebuild_source(sender, 'save')
    logger.info('Astro rebuild planlandı: %s (pk=%s)', source, getattr(instance, 'pk', None))
    trigger_astro_rebuild(source=source, updated_at=updated_at)


def _on_delete(sender, instance, **kwargs):
    source = _rebuild_source(sender, 'delete')
    logger.info('Astro rebuild planlandı: %s (pk=%s)', source, getattr(instance, 'pk', None))
    trigger_astro_rebuild(source=source)


def connect_astro_rebuild_signals() -> None:
    connected = 0
    for app_label, model_name in ASTRO_REBUILD_MODELS:
        sender = f'{app_label}.{model_name}'
        # String sender: AppConfig.ready() sırasında model çözümlemesi güvenli.
        apps.get_model(app_label, model_name)
        post_save.connect(
            _on_save,
            sender=sender,
            dispatch_uid=f'astro-rebuild-save-{sender}',
        )
        post_delete.connect(
            _on_delete,
            sender=sender,
            dispatch_uid=f'astro-rebuild-delete-{sender}',
        )
        connected += 1
    logger.info('Astro rebuild sinyalleri kayıtlı: %d model', connected)
