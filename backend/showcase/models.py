from django.core.exceptions import ValidationError
from django.db import models
from django_prose_editor.fields import ProseEditorField

from localization.mixins import TranslatableMixin

from core.editor import SHOWCASE_SECTION_DESCRIPTION_EXTENSIONS


class ShowcaseStat(TranslatableMixin, models.Model):
    """Hizmetler bölümü üstündeki istatistik kartları."""

    value = models.CharField(
        'Değer',
        max_length=40,
        help_text='Örn: 7/24, 15 dk, 5000+',
    )
    label = models.CharField(
        'Etiket',
        max_length=120,
        help_text='Örn: Kesintisiz Hizmet, Ortalama Varış',
    )
    order = models.PositiveIntegerField('Sıra', default=0)
    is_active = models.BooleanField('Aktif', default=True)

    class Meta:
        verbose_name = 'Vitrin istatistiği'
        verbose_name_plural = 'Vitrin istatistikleri'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.value} — {self.label}'


class ShowcaseStatTranslation(models.Model):
    stat = models.ForeignKey(
        ShowcaseStat,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name='İstatistik',
    )
    language = models.ForeignKey(
        'localization.Language',
        on_delete=models.CASCADE,
        related_name='showcase_stat_translations',
        verbose_name='Dil',
    )
    value = models.CharField('Değer', max_length=40, blank=True)
    label = models.CharField('Etiket', max_length=120, blank=True)

    class Meta:
        verbose_name = 'Vitrin istatistiği çevirisi'
        verbose_name_plural = 'Vitrin istatistiği çevirileri'
        constraints = [
            models.UniqueConstraint(
                fields=['stat', 'language'],
                name='unique_showcase_stat_translation_per_language',
            ),
        ]

    def __str__(self):
        return f'{self.stat_id} [{self.language.code}]'


class ShowcaseServiceSection(TranslatableMixin, models.Model):
    """Hizmetler bölümü başlık alanı (tekil)."""

    badge = models.CharField(
        'Üst etiket',
        max_length=120,
        default='Neden Çekici Pro?',
        help_text='H2 üstündeki küçük amber etiket.',
    )
    title = models.CharField(
        'Başlık (H2)',
        max_length=200,
        default='Kapsamlı Yol Yardım Hizmetleri',
    )
    description = ProseEditorField(
        'Açıklama',
        blank=True,
        extensions=SHOWCASE_SECTION_DESCRIPTION_EXTENSIONS,
        sanitize=True,
        help_text='H2 altı paragraf. Yer tutucular: {business_name}, {region}',
    )

    class Meta:
        verbose_name = 'Hizmetler bölümü'
        verbose_name_plural = 'Hizmetler bölümü'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Hizmetler bölümü ayarları silinemez.')

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'badge': 'Neden Çekici Pro?',
                'title': 'Kapsamlı Yol Yardım Hizmetleri',
                'description': (
                    '<p>{region} bölgesinde oto çekici, acil yol yardım ve mobil tamir '
                    'hizmetleri sunuyoruz. Her hizmetimiz lisanslı ekip ve sigortalı taşıma '
                    'garantisiyle sunulur.</p>'
                ),
            },
        )
        return obj


class ShowcaseServiceSectionTranslation(models.Model):
    section = models.ForeignKey(
        ShowcaseServiceSection,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name='Hizmetler bölümü',
    )
    language = models.ForeignKey(
        'localization.Language',
        on_delete=models.CASCADE,
        related_name='showcase_section_translations',
        verbose_name='Dil',
    )
    badge = models.CharField('Üst etiket', max_length=120, blank=True)
    title = models.CharField('Başlık', max_length=200, blank=True)
    description = ProseEditorField(
        'Açıklama',
        blank=True,
        extensions=SHOWCASE_SECTION_DESCRIPTION_EXTENSIONS,
        sanitize=True,
    )

    class Meta:
        verbose_name = 'Hizmetler bölümü çevirisi'
        verbose_name_plural = 'Hizmetler bölümü çevirileri'
        constraints = [
            models.UniqueConstraint(
                fields=['section', 'language'],
                name='unique_showcase_section_translation_per_language',
            ),
        ]

    def __str__(self):
        return f'Bölüm [{self.language.code}]'


class ShowcaseService(TranslatableMixin, models.Model):
    """Hizmetler bölümündeki kartlar."""

    icon = models.CharField(
        'İkon (emoji)',
        max_length=16,
        help_text='Örn: 🚗, 🛟',
    )
    title = models.CharField('Başlık', max_length=120)
    description = models.TextField('Açıklama')
    order = models.PositiveIntegerField('Sıra', default=0)
    is_active = models.BooleanField('Aktif', default=True)

    class Meta:
        verbose_name = 'Hizmet kartı'
        verbose_name_plural = 'Hizmet kartları'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class ShowcaseServiceTranslation(models.Model):
    service = models.ForeignKey(
        ShowcaseService,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name='Hizmet kartı',
    )
    language = models.ForeignKey(
        'localization.Language',
        on_delete=models.CASCADE,
        related_name='showcase_service_translations',
        verbose_name='Dil',
    )
    title = models.CharField('Başlık', max_length=120, blank=True)
    description = models.TextField('Açıklama', blank=True)

    class Meta:
        verbose_name = 'Hizmet kartı çevirisi'
        verbose_name_plural = 'Hizmet kartı çevirileri'
        constraints = [
            models.UniqueConstraint(
                fields=['service', 'language'],
                name='unique_showcase_service_translation_per_language',
            ),
        ]

    def __str__(self):
        return f'{self.service_id} [{self.language.code}]'
