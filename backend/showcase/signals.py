from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from core.services.astro_rebuild import trigger_astro_rebuild

from .models import ShowcaseService, ShowcaseServiceSection, ShowcaseStat


@receiver(post_save, sender=ShowcaseStat)
def on_showcase_stat_saved(sender, instance, **kwargs):
    trigger_astro_rebuild(source='showcase_stat_save')


@receiver(post_delete, sender=ShowcaseStat)
def on_showcase_stat_deleted(sender, instance, **kwargs):
    trigger_astro_rebuild(source='showcase_stat_delete')


@receiver(post_save, sender=ShowcaseServiceSection)
def on_showcase_section_saved(sender, instance, **kwargs):
    trigger_astro_rebuild(source='showcase_service_section_save')


@receiver(post_save, sender=ShowcaseService)
def on_showcase_service_saved(sender, instance, **kwargs):
    trigger_astro_rebuild(source='showcase_service_save')


@receiver(post_delete, sender=ShowcaseService)
def on_showcase_service_deleted(sender, instance, **kwargs):
    trigger_astro_rebuild(source='showcase_service_delete')
