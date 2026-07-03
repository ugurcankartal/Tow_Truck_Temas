from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from core.services.astro_rebuild import trigger_astro_rebuild

from .models import SiteImage, SiteImagePlacement


@receiver(post_save, sender=SiteImage)
def on_site_image_saved(sender, instance, **kwargs):
    trigger_astro_rebuild(source='site_image_save')


@receiver(post_delete, sender=SiteImage)
def on_site_image_deleted(sender, instance, **kwargs):
    trigger_astro_rebuild(source='site_image_delete')


@receiver(post_save, sender=SiteImagePlacement)
def on_placement_saved(sender, instance, **kwargs):
    trigger_astro_rebuild(source='image_placement_save')


@receiver(post_delete, sender=SiteImagePlacement)
def on_placement_deleted(sender, instance, **kwargs):
    trigger_astro_rebuild(source='image_placement_delete')
