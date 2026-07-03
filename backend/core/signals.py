from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import FAQ, SiteSettings
from .services.astro_rebuild import trigger_astro_rebuild


@receiver(post_save, sender=SiteSettings)
def on_site_settings_saved(sender, instance, **kwargs):
    trigger_astro_rebuild(
        source='site_settings',
        updated_at=instance.updated_at.isoformat() if instance.updated_at else None,
    )


@receiver(post_save, sender=FAQ)
def on_faq_saved(sender, instance, **kwargs):
    trigger_astro_rebuild(source='faq_save')


@receiver(post_delete, sender=FAQ)
def on_faq_deleted(sender, instance, **kwargs):
    trigger_astro_rebuild(source='faq_delete')
