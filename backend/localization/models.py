from django.db import models, transaction


class Language(models.Model):
    """Admin üzerinden yönetilen diller."""

    code = models.CharField(
        max_length=16,
        unique=True,
        verbose_name='Kod',
        help_text='BCP47, örn: tr, en',
    )
    name_native = models.CharField(max_length=64, verbose_name='Yerel ad')
    flag = models.ImageField(
        upload_to='languages/flags/',
        blank=True,
        null=True,
        verbose_name='Bayrak',
    )
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    is_default = models.BooleanField(
        default=False,
        verbose_name='Varsayılan',
        help_text='Aynı anda yalnızca bir dil varsayılan olabilir.',
    )
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='Sıra')

    class Meta:
        ordering = ['sort_order', 'code']
        verbose_name = 'Dil'
        verbose_name_plural = 'Diller'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.is_default:
                (
                    Language.objects.filter(is_default=True)
                    .exclude(pk=self.pk)
                    .update(is_default=False)
                )
            super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.code} — {self.name_native}'


class UiStringKey(models.Model):
    """Frontend sabit anahtarları (örn. nav.home)."""

    key = models.CharField(max_length=190, unique=True, db_index=True)
    help_text = models.TextField(blank=True)

    class Meta:
        ordering = ['key']
        verbose_name = 'UI metin anahtarı'
        verbose_name_plural = 'UI metin anahtarları'

    def __str__(self) -> str:
        return self.key


class UiString(models.Model):
    """UiStringKey için dil bazlı metin."""

    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name='ui_strings',
        verbose_name='Dil',
    )
    key = models.ForeignKey(
        UiStringKey,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name='Anahtar',
    )
    text = models.TextField(verbose_name='Metin')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['language', 'key'],
                name='uniq_uistring_lang_key',
            ),
        ]
        verbose_name = 'UI çevirisi'
        verbose_name_plural = 'UI çevirileri'

    def __str__(self) -> str:
        return f'{self.language.code}:{self.key.key}'
