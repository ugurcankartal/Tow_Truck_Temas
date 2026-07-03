import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from localization.mixins import TranslatableMixin


class ContentZone(TranslatableMixin, models.Model):
    """Sayfa bölümleri — görsellerin hangi alanda gösterileceğini tanımlar."""

    CODE_HERO = 'hero'
    CODE_SCROLL_DRAW = 'scroll_draw'

    code = models.SlugField('Kod', max_length=50, unique=True)
    name = models.CharField('Bölüm adı', max_length=100)
    description = models.TextField('Açıklama', blank=True)

    class Meta:
        db_table = 'core_contentzone'
        verbose_name = 'İçerik bölgesi'
        verbose_name_plural = 'İçerik bölgeleri'
        ordering = ['id']

    def __str__(self):
        return self.name


class ContentZoneTranslation(models.Model):
    zone = models.ForeignKey(
        ContentZone,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name='Bölge',
    )
    language = models.ForeignKey(
        'localization.Language',
        on_delete=models.CASCADE,
        related_name='content_zone_translations',
        verbose_name='Dil',
    )
    name = models.CharField('Bölüm adı', max_length=100, blank=True)
    description = models.TextField('Açıklama', blank=True)

    class Meta:
        db_table = 'core_contentzone_translation'
        verbose_name = 'İçerik bölgesi çevirisi'
        verbose_name_plural = 'İçerik bölgesi çevirileri'
        constraints = [
            models.UniqueConstraint(
                fields=['zone', 'language'],
                name='unique_content_zone_translation_per_language',
            ),
        ]

    def __str__(self):
        return f'{self.zone.code} [{self.language.code}]'


class SiteImage(TranslatableMixin, models.Model):
    """Site genelinde kullanılabilen görsel havuzu."""

    image = models.ImageField(
        'Yüklenen görsel',
        upload_to='site_images/%Y/%m/',
        blank=True,
        help_text='Yüklü görsel varsa API ve sitede bu kullanılır.',
    )
    image_url = models.URLField(
        'Görsel URL',
        max_length=500,
        blank=True,
        help_text='Yüklü görsel yoksa bu URL kullanılır.',
    )
    title = models.CharField('Başlık', max_length=120)
    subtitle = models.CharField(
        'Alt başlık',
        max_length=200,
        blank=True,
        help_text='Hero slayt üst satırı.',
    )
    description = models.TextField(
        'Açıklama',
        blank=True,
        help_text='Scroll-draw alt metni.',
    )
    alt_text = models.CharField('Görsel alt metni (SEO)', max_length=200)
    is_active = models.BooleanField('Aktif', default=True)

    zones = models.ManyToManyField(
        ContentZone,
        through='SiteImagePlacement',
        related_name='images',
        verbose_name='Gösterim bölgeleri',
    )

    class Meta:
        db_table = 'core_siteimage'
        verbose_name = 'Site görseli'
        verbose_name_plural = 'Site görselleri'
        ordering = ['id']

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if not self.image and not self.image_url:
            raise ValidationError(
                'Görsel URL veya yüklenen görselden en az biri zorunludur.'
            )

    def get_resolved_url(self, request=None) -> str:
        """Yüklü görsel öncelikli; yoksa image_url döner."""
        if self.image:
            url = self.image.url
            if request is not None:
                return request.build_absolute_uri(url)
            api_base = os.environ.get(
                'PUBLIC_API_URL',
                getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
            ).rstrip('/')
            return f'{api_base}{url}' if url.startswith('/') else url
        return self.image_url or ''

    @property
    def zone_labels(self):
        return ', '.join(
            self.placements.filter(is_active=True).values_list('zone__name', flat=True)
        )


class SiteImageTranslation(models.Model):
    site_image = models.ForeignKey(
        SiteImage,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name='Görsel',
    )
    language = models.ForeignKey(
        'localization.Language',
        on_delete=models.CASCADE,
        related_name='site_image_translations',
        verbose_name='Dil',
    )
    title = models.CharField('Başlık', max_length=120, blank=True)
    subtitle = models.CharField('Alt başlık', max_length=200, blank=True)
    description = models.TextField('Açıklama', blank=True)
    alt_text = models.CharField('Alt metin', max_length=200, blank=True)

    class Meta:
        db_table = 'core_siteimage_translation'
        verbose_name = 'Site görseli çevirisi'
        verbose_name_plural = 'Site görseli çevirileri'
        constraints = [
            models.UniqueConstraint(
                fields=['site_image', 'language'],
                name='unique_site_image_translation_per_language',
            ),
        ]

    def __str__(self):
        return f'{self.site_image_id} [{self.language.code}]'


class SiteImagePlacement(models.Model):
    """Görsel ↔ bölge ilişkisi (M2M ara tablo). Sıra ve aktiflik bölüme özeldir."""

    site_image = models.ForeignKey(
        SiteImage,
        on_delete=models.CASCADE,
        related_name='placements',
        verbose_name='Görsel',
    )
    zone = models.ForeignKey(
        ContentZone,
        on_delete=models.CASCADE,
        related_name='placements',
        verbose_name='Bölge',
    )
    order = models.PositiveIntegerField('Sıra', default=0)
    is_active = models.BooleanField('Aktif', default=True)

    class Meta:
        db_table = 'core_siteimageplacement'
        verbose_name = 'Görsel konumu'
        verbose_name_plural = 'Görsel konumları'
        ordering = ['zone', 'order', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['site_image', 'zone'],
                name='unique_image_per_zone',
            ),
        ]

    def __str__(self):
        return f'{self.site_image.title} → {self.zone.name} (#{self.order})'
