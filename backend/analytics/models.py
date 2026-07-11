from django.db import models


class SiteVisit(models.Model):
    """Site ziyaretçilerinin ağ, konum, cihaz ve oturum bilgileri."""

    class DeviceType(models.TextChoices):
        DESKTOP = 'desktop', 'Masaüstü'
        MOBILE = 'mobile', 'Mobil'
        TABLET = 'tablet', 'Tablet'
        BOT = 'bot', 'Bot'
        OTHER = 'other', 'Diğer'

    class VisitSource(models.TextChoices):
        PUBLIC = 'public', 'Ön yüz'
        ADMIN = 'admin', 'Admin panel'

    ip_address = models.GenericIPAddressField('IP adresi', null=True, blank=True, db_index=True)

    country = models.CharField('Ülke', max_length=100, blank=True)
    country_code = models.CharField('Ülke kodu', max_length=2, blank=True)
    region = models.CharField('Bölge / il', max_length=100, blank=True)
    city = models.CharField('Şehir', max_length=100, blank=True)
    postal_code = models.CharField('Posta kodu', max_length=20, blank=True)
    location_address = models.TextField(
        'Konum adresi',
        blank=True,
        help_text='IP coğrafi konumundan üretilen okunabilir adres özeti.',
    )
    latitude = models.DecimalField(
        'Enlem', max_digits=9, decimal_places=6, null=True, blank=True,
    )
    longitude = models.DecimalField(
        'Boylam', max_digits=9, decimal_places=6, null=True, blank=True,
    )
    timezone = models.CharField('Saat dilimi', max_length=64, blank=True)
    isp = models.CharField('İnternet servis sağlayıcı', max_length=255, blank=True)

    host = models.CharField('Host', max_length=255, blank=True)
    path = models.CharField('Sayfa yolu', max_length=500, blank=True, db_index=True)
    full_url = models.URLField('Tam URL', max_length=2000, blank=True)
    referrer = models.URLField('Referrer', max_length=2000, blank=True)
    http_method = models.CharField('HTTP metodu', max_length=10, default='GET')
    accept_language = models.CharField('Dil tercihi', max_length=255, blank=True)

    user_agent = models.TextField('User-Agent', blank=True)
    device_type = models.CharField(
        'Cihaz tipi',
        max_length=20,
        choices=DeviceType.choices,
        blank=True,
        db_index=True,
    )
    device_brand = models.CharField('Cihaz markası', max_length=64, blank=True)
    device_model = models.CharField('Cihaz modeli', max_length=128, blank=True)
    browser = models.CharField('Tarayıcı', max_length=64, blank=True)
    browser_version = models.CharField('Tarayıcı sürümü', max_length=32, blank=True)
    os_name = models.CharField('İşletim sistemi', max_length=64, blank=True)
    os_version = models.CharField('OS sürümü', max_length=32, blank=True)
    is_bot = models.BooleanField('Bot', default=False, db_index=True)

    screen_width = models.PositiveIntegerField('Ekran genişliği', null=True, blank=True)
    screen_height = models.PositiveIntegerField('Ekran yüksekliği', null=True, blank=True)
    viewport_width = models.PositiveIntegerField('Viewport genişliği', null=True, blank=True)
    viewport_height = models.PositiveIntegerField('Viewport yüksekliği', null=True, blank=True)

    session_key = models.CharField('Oturum anahtarı', max_length=64, blank=True, db_index=True)
    visitor_key = models.CharField('Ziyaretçi anahtarı', max_length=64, blank=True, db_index=True)

    visit_source = models.CharField(
        'Kaynak',
        max_length=20,
        choices=VisitSource.choices,
        default=VisitSource.PUBLIC,
        db_index=True,
    )
    is_staff_session = models.BooleanField(
        'Yetkili oturum',
        default=False,
        db_index=True,
        help_text='Admin panelde giriş yapmış staff kullanıcı.',
    )
    staff_username = models.CharField(
        'Staff kullanıcı',
        max_length=150,
        blank=True,
        db_index=True,
    )

    visited_at = models.DateTimeField('Ziyaret zamanı', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Site ziyareti'
        verbose_name_plural = 'Site ziyaretleri'
        ordering = ['-visited_at']
        indexes = [
            models.Index(fields=['-visited_at', 'country']),
            models.Index(fields=['ip_address', '-visited_at']),
            models.Index(fields=['city', '-visited_at']),
        ]

    def __str__(self):
        location = self.city or self.country or 'Bilinmiyor'
        return f'{self.ip_address or "?"} — {location} ({self.visited_at:%Y-%m-%d %H:%M})'
