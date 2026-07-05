import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django_prose_editor.fields import ProseEditorField

from localization.mixins import TranslatableMixin

from .editor import HERO_INTRO_BODY_EXTENSIONS, HERO_INTRO_TITLE_EXTENSIONS


class SiteSettings(TranslatableMixin, models.Model):
    """
    Tekil site ayarları (singleton).
    Astro build ve JSON-LD için SEO/GEO + işletme (NAP) verileri.
    """

    # --- SEO / GEO meta ---
    meta_title = models.CharField(
        'Sayfa başlığı (title)',
        max_length=120,
        help_text='Önerilen: 70 karakter altı (Google snippet). Maks. 120.',
    )
    meta_description = models.CharField(
        'Meta açıklama',
        max_length=320,
        help_text='Önerilen: 160 karakter altı. Maks. 320.',
    )
    meta_keywords = models.CharField(
        'Anahtar kelimeler',
        max_length=500,
        blank=True,
        help_text='Virgülle ayrılmış anahtar kelimeler. Maks. 500.',
    )
    canonical_url = models.URLField('Canonical URL', max_length=255)
    og_image_url = models.URLField('OG görsel URL', max_length=500, blank=True)
    robots = models.CharField(
        'Robots',
        max_length=255,
        default='index, follow',
        help_text='Örn: index, follow | noindex, nofollow | max-snippet:-1, max-image-preview:large',
    )

    # --- İşletme (NAP) ---
    business_name = models.CharField('İşletme adı', max_length=100)
    legal_name = models.CharField('Yasal unvan', max_length=150)
    tagline = models.CharField('Slogan', max_length=120)
    email = models.EmailField('E-posta')

    street = models.CharField('Adres (sokak)', max_length=200)
    district = models.CharField('İlçe', max_length=100)
    city = models.CharField('Şehir', max_length=100)
    region = models.CharField('Bölge', max_length=100)
    postal_code = models.CharField('Posta kodu', max_length=10)
    country = models.CharField('Ülke kodu', max_length=2, default='TR')

    latitude = models.DecimalField('Enlem', max_digits=9, decimal_places=6)
    longitude = models.DecimalField('Boylam', max_digits=9, decimal_places=6)

    opening_hours = models.CharField('Çalışma saatleri (schema)', max_length=100, default='Mo-Su 00:00-23:59')
    price_range = models.CharField(
        'Fiyat aralığı',
        max_length=50,
        default='₺₺',
        help_text='Schema.org priceRange. Örn: ₺₺, ₺₺₺ veya kısa açıklama.',
    )
    area_served = models.JSONField('Hizmet bölgeleri', default=list, blank=True)

    instagram_url = models.URLField('Instagram', max_length=255, blank=True)
    facebook_url = models.URLField('Facebook', max_length=255, blank=True)

    # --- Marka ---
    logo = models.ImageField(
        'Yüklenen logo',
        upload_to='site_logo/%Y/%m/',
        blank=True,
        help_text='Yüklü logo varsa navigatörde bu kullanılır.',
    )
    logo_url = models.URLField(
        'Logo URL',
        max_length=500,
        blank=True,
        help_text='Yüklü logo yoksa bu URL kullanılır.',
    )
    favicon = models.FileField(
        'Yüklenen favicon',
        upload_to='site_favicon/%Y/%m/',
        blank=True,
        help_text='Tarayıcı sekmesi ikonu (.ico, .png, .svg). Yüklü dosya önceliklidir.',
    )
    favicon_url = models.URLField(
        'Favicon URL',
        max_length=500,
        blank=True,
        help_text='Yüklü favicon yoksa bu URL kullanılır.',
    )

    site_url = models.URLField('Site URL', max_length=255)

    footer_copyright = models.CharField(
        'Footer telif metni',
        max_length=255,
        default='© {year} {legal_name}. Tüm hakları saklıdır.',
        help_text='Alt bilgi satırı. Kullanılabilir: {year}, {legal_name}',
    )

    # --- Hero giriş (slider altı) ---
    hero_intro_badge = models.CharField(
        'Hero rozet metni',
        max_length=80,
        default='Aktif Hizmet',
        help_text='Başlık üstündeki küçük etiket.',
    )
    hero_intro_title = ProseEditorField(
        'Hero başlık (H1)',
        blank=True,
        extensions=HERO_INTRO_TITLE_EXTENSIONS,
        sanitize=True,
        help_text=(
            'Ana başlık. Yer tutucular: {business_name}, {region}. '
            'Vurgulu gradient metin: {accent}Yol Yardım{/accent}'
        ),
    )
    hero_intro_body = ProseEditorField(
        'Hero giriş metni',
        blank=True,
        extensions=HERO_INTRO_BODY_EXTENSIONS,
        sanitize=True,
        help_text=(
            'Sağ sütun paragrafları. Yer tutucular: {business_name}, {region}. '
            'CTA butonu şablonda sabittir.'
        ),
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Ayarları'
        verbose_name_plural = 'Site Ayarları'

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Site ayarları silinemez.')

    def _resolve_media_url(self, file_field: str, url_field: str, request=None) -> str:
        uploaded = getattr(self, file_field)
        if uploaded:
            url = uploaded.url
            if request is not None:
                return request.build_absolute_uri(url)
            api_base = os.environ.get(
                'PUBLIC_API_URL',
                getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
            ).rstrip('/')
            return f'{api_base}{url}' if url.startswith('/') else url
        return getattr(self, url_field) or ''

    def get_resolved_logo_url(self, request=None) -> str:
        return self._resolve_media_url('logo', 'logo_url', request)

    def get_resolved_favicon_url(self, request=None) -> str:
        return self._resolve_media_url('favicon', 'favicon_url', request)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'meta_title': 'Çekici Pro | İstanbul Anadolu Yakası 7/24 Oto Çekici',
                'meta_description': (
                    'İstanbul Anadolu Yakası 7/24 oto çekici ve yol yardım hizmeti.'
                ),
                'canonical_url': 'https://cekicipro.com/',
                'business_name': 'Çekici Pro',
                'legal_name': 'Çekici Pro Oto Kurtarma Ltd. Şti.',
                'tagline': '7/24 Oto Çekici & Yol Yardım',
                'email': 'info@cekicipro.com',
                'street': 'Atatürk Cad. No: 142',
                'district': 'Kadıköy',
                'city': 'İstanbul',
                'region': 'Anadolu Yakası',
                'postal_code': '34710',
                'latitude': 40.990100,
                'longitude': 29.029200,
                'area_served': [
                    'Kadıköy', 'Üsküdar', 'Ataşehir', 'Maltepe', 'Kartal', 'Pendik',
                ],
                'site_url': 'https://cekicipro.com',
                'footer_copyright': '© {year} {legal_name}. Tüm hakları saklıdır.',
                'hero_intro_badge': 'Aktif Hizmet',
                'hero_intro_title': (
                    '<p>İstanbul Anadolu Yakası 7/24 Oto Çekici &amp; '
                    '{accent}Yol Yardım{/accent}</p>'
                ),
                'hero_intro_body': (
                    '<p><strong>{business_name}</strong> olarak {region} genelinde '
                    '7 gün 24 saat profesyonel oto çekici ve yol yardım hizmeti sunuyoruz. '
                    'Deneyimli ekibimiz ve modern ekipmanlarımızla aracınızı en kısa sürede '
                    'güvenle taşıyoruz.</p>'
                    '<p>Oto kurtarma, akü takviyesi, lastik değişimi ve acil yol yardım '
                    'ihtiyaçlarınız için tek numara — hızlı, şeffaf fiyatlandırma ve müşteri '
                    'memnuniyeti odaklı hizmet.</p>'
                ),
            },
        )
        return obj


class SiteSettingsTranslation(models.Model):
    """Site ayarları — dil bazlı metin alanları."""

    settings = models.ForeignKey(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name='Site ayarları',
    )
    language = models.ForeignKey(
        'localization.Language',
        on_delete=models.CASCADE,
        related_name='site_settings_translations',
        verbose_name='Dil',
    )
    meta_title = models.CharField('Sayfa başlığı', max_length=120, blank=True)
    meta_description = models.CharField('Meta açıklama', max_length=320, blank=True)
    meta_keywords = models.CharField('Anahtar kelimeler', max_length=500, blank=True)
    business_name = models.CharField('İşletme adı', max_length=100, blank=True)
    legal_name = models.CharField('Yasal unvan', max_length=150, blank=True)
    tagline = models.CharField('Slogan', max_length=120, blank=True)
    street = models.CharField('Adres (sokak)', max_length=200, blank=True)
    district = models.CharField('İlçe', max_length=100, blank=True)
    city = models.CharField('Şehir', max_length=100, blank=True)
    region = models.CharField('Bölge', max_length=100, blank=True)
    footer_copyright = models.CharField('Footer telif', max_length=255, blank=True)
    hero_intro_badge = models.CharField('Hero rozet', max_length=80, blank=True)
    hero_intro_title = ProseEditorField(
        'Hero başlık',
        blank=True,
        extensions=HERO_INTRO_TITLE_EXTENSIONS,
        sanitize=True,
    )
    hero_intro_body = ProseEditorField(
        'Hero giriş metni',
        blank=True,
        extensions=HERO_INTRO_BODY_EXTENSIONS,
        sanitize=True,
    )
    area_served = models.JSONField('Hizmet bölgeleri', default=list, blank=True)

    class Meta:
        verbose_name = 'Site ayarı çevirisi'
        verbose_name_plural = 'Site ayarı çevirileri'
        constraints = [
            models.UniqueConstraint(
                fields=['settings', 'language'],
                name='unique_site_settings_translation_per_language',
            ),
        ]

    def __str__(self):
        return f'{self.settings} [{self.language.code}]'


class SiteContact(TranslatableMixin, models.Model):
    """Site ayarlarına bağlı iletişim satırı (telefon, e-posta, URL vb.)."""

    TYPE_PHONE = 'phone'
    TYPE_EMAIL = 'email'
    TYPE_URL = 'url'
    TYPE_TEXT = 'text'
    TYPE_CHOICES = [
        (TYPE_PHONE, 'Telefon'),
        (TYPE_EMAIL, 'E-posta'),
        (TYPE_URL, 'Web / URL'),
        (TYPE_TEXT, 'Metin'),
    ]

    settings = models.ForeignKey(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name='Site ayarları',
    )
    contact_type = models.CharField(
        'Tür',
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_PHONE,
    )
    label = models.CharField(
        'Etiket',
        max_length=120,
        help_text='Örn: Telefon, WhatsApp, Acil hat',
    )
    value = models.CharField('Değer', max_length=255)
    order = models.PositiveIntegerField('Sıra', default=0)
    is_active = models.BooleanField('Aktif', default=True)
    is_primary = models.BooleanField(
        'Birincil (nav/hero/CTA)',
        default=False,
        help_text='Üst menü, hero ve footer CTA için kullanılır.',
    )

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'İletişim'
        verbose_name_plural = 'İletişim bilgileri'

    def __str__(self):
        return f'{self.label}: {self.value}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_primary:
            SiteContact.objects.filter(
                settings=self.settings,
                is_primary=True,
            ).exclude(pk=self.pk).update(is_primary=False)
        self._sync_default_translation_label()

    def _sync_default_translation_label(self):
        """Inline'da düzenlenen etiket varsayılan dil çevirisine yansır."""
        from localization.models import Language

        default_lang = Language.objects.filter(is_active=True, is_default=True).first()
        if not default_lang:
            default_lang = Language.objects.filter(is_active=True, code='tr').first()
        if not default_lang:
            return
        SiteContactTranslation.objects.update_or_create(
            contact=self,
            language=default_lang,
            defaults={'label': self.label},
        )


class SiteContactTranslation(models.Model):
    contact = models.ForeignKey(
        SiteContact,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name='İletişim',
    )
    language = models.ForeignKey(
        'localization.Language',
        on_delete=models.CASCADE,
        related_name='site_contact_translations',
        verbose_name='Dil',
    )
    label = models.CharField('Etiket', max_length=120, blank=True)

    class Meta:
        verbose_name = 'İletişim çevirisi'
        verbose_name_plural = 'İletişim çevirileri'
        constraints = [
            models.UniqueConstraint(
                fields=['contact', 'language'],
                name='unique_site_contact_translation_per_language',
            ),
        ]

    def __str__(self):
        return f'{self.contact_id} [{self.language.code}]'


class FAQ(TranslatableMixin, models.Model):
    question = models.CharField('Soru', max_length=300)
    answer = models.TextField('Cevap')
    order = models.PositiveIntegerField('Sıra', default=0)
    is_active = models.BooleanField('Aktif', default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'SSS'
        verbose_name_plural = 'SSS'

    def __str__(self):
        return self.question


class FAQTranslation(models.Model):
    faq = models.ForeignKey(
        FAQ,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name='SSS',
    )
    language = models.ForeignKey(
        'localization.Language',
        on_delete=models.CASCADE,
        related_name='faq_translations',
        verbose_name='Dil',
    )
    question = models.CharField('Soru', max_length=300, blank=True)
    answer = models.TextField('Cevap', blank=True)

    class Meta:
        verbose_name = 'SSS çevirisi'
        verbose_name_plural = 'SSS çevirileri'
        constraints = [
            models.UniqueConstraint(
                fields=['faq', 'language'],
                name='unique_faq_translation_per_language',
            ),
        ]

    def __str__(self):
        return f'{self.faq_id} [{self.language.code}]'


class ContactMessage(models.Model):
    name = models.CharField('Ad Soyad', max_length=100)
    phone = models.CharField('Telefon', max_length=20)
    message = models.TextField('Mesaj')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField('Okundu', default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'İletişim Mesajı'
        verbose_name_plural = 'İletişim Mesajları'

    def __str__(self):
        return f'{self.name} — {self.phone}'
