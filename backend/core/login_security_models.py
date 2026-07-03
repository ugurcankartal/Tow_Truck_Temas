from django.db import models


class AdminLoginSecuritySettings(models.Model):
    """Admin giriş kilitleme kuralları (tekil)."""

    window_minutes = models.PositiveSmallIntegerField(
        'Pencere süresi (dk)',
        default=5,
        help_text='Hatalı denemelerin sayıldığı süre.',
    )
    max_attempts = models.PositiveSmallIntegerField(
        'Maks. hatalı deneme',
        default=3,
        help_text='Bu sayıya ulaşılınca ceza uygulanır.',
    )
    lockout_minutes = models.PositiveSmallIntegerField(
        'Ceza süresi (dk)',
        default=5,
        help_text='Kilitlenme süresi.',
    )
    updated_at = models.DateTimeField('Güncellendi', auto_now=True)

    class Meta:
        verbose_name = 'Admin giriş güvenlik ayarı'
        verbose_name_plural = 'Admin giriş güvenlik ayarları'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self) -> str:
        return (
            f'{self.max_attempts} deneme / {self.window_minutes} dk → '
            f'{self.lockout_minutes} dk ceza'
        )


class AdminLoginFailedAttempt(models.Model):
    username = models.CharField('Kullanıcı adı', max_length=150, db_index=True)
    device_key = models.CharField('Cihaz anahtarı', max_length=64, db_index=True)
    ip_address = models.GenericIPAddressField('IP', null=True, blank=True)
    user_agent = models.TextField('User-Agent', blank=True)
    created_at = models.DateTimeField('Tarih', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Admin hatalı giriş denemesi'
        verbose_name_plural = 'Admin hatalı giriş denemeleri'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username', '-created_at']),
            models.Index(fields=['device_key', '-created_at']),
        ]

    def __str__(self) -> str:
        return f'{self.username} @ {self.created_at:%Y-%m-%d %H:%M}'


class AdminLoginUsernameLock(models.Model):
    username = models.CharField('Kullanıcı adı', max_length=150, unique=True, db_index=True)
    locked_until = models.DateTimeField('Kilit bitiş')
    created_at = models.DateTimeField('Oluşturuldu', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellendi', auto_now=True)

    class Meta:
        verbose_name = 'Admin kullanıcı adı kilidi'
        verbose_name_plural = 'Admin kullanıcı adı kilitleri'
        ordering = ['-locked_until']

    def __str__(self) -> str:
        return f'{self.username} → {self.locked_until:%Y-%m-%d %H:%M}'


class AdminLoginDeviceLock(models.Model):
    device_key = models.CharField('Cihaz anahtarı', max_length=64, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField('Son IP', null=True, blank=True)
    user_agent = models.TextField('Son User-Agent', blank=True)
    locked_until = models.DateTimeField('Kilit bitiş')
    created_at = models.DateTimeField('Oluşturuldu', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellendi', auto_now=True)

    class Meta:
        verbose_name = 'Admin cihaz kilidi'
        verbose_name_plural = 'Admin cihaz kilitleri'
        ordering = ['-locked_until']

    def __str__(self) -> str:
        return f'{self.device_key[:12]}… → {self.locked_until:%Y-%m-%d %H:%M}'
