"""SiteContact modeli; SiteSettings.phone → iletişim satırları."""

from django.db import migrations, models
import django.db.models.deletion


def migrate_phone_to_contacts(apps, schema_editor):
    SiteSettings = apps.get_model('core', 'SiteSettings')
    SiteContact = apps.get_model('core', 'SiteContact')
    Language = apps.get_model('localization', 'Language')

    settings = SiteSettings.objects.filter(pk=1).first()
    if not settings:
        return

    phone = getattr(settings, 'phone', '') or ''
    if not phone.strip():
        return

    if SiteContact.objects.filter(settings=settings).exists():
        return

    contact = SiteContact.objects.create(
        settings=settings,
        contact_type='phone',
        label='Telefon',
        value=phone.strip(),
        order=0,
        is_active=True,
        is_primary=True,
    )

    tr = Language.objects.filter(code='tr', is_active=True).first()
    en = Language.objects.filter(code='en', is_active=True).first()
    SiteContactTranslation = apps.get_model('core', 'SiteContactTranslation')
    if tr:
        SiteContactTranslation.objects.get_or_create(
            contact=contact,
            language=tr,
            defaults={'label': 'Telefon'},
        )
    if en:
        SiteContactTranslation.objects.get_or_create(
            contact=contact,
            language=en,
            defaults={'label': 'Phone'},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('localization', '0003_migrate_content_translations'),
        ('core', '0014_admin_login_security'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_type', models.CharField(
                    choices=[('phone', 'Telefon'), ('email', 'E-posta'), ('url', 'Web / URL'), ('text', 'Metin')],
                    default='phone',
                    max_length=20,
                    verbose_name='Tür',
                )),
                ('label', models.CharField(
                    help_text='Örn: Telefon, WhatsApp, Acil hat',
                    max_length=120,
                    verbose_name='Etiket',
                )),
                ('value', models.CharField(max_length=255, verbose_name='Değer')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Sıra')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
                ('is_primary', models.BooleanField(
                    default=False,
                    help_text='Üst menü, hero ve footer CTA için kullanılır.',
                    verbose_name='Birincil (nav/hero/CTA)',
                )),
                ('settings', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='contacts',
                    to='core.sitesettings',
                    verbose_name='Site ayarları',
                )),
            ],
            options={
                'verbose_name': 'İletişim',
                'verbose_name_plural': 'İletişim bilgileri',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='SiteContactTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=120, verbose_name='Etiket')),
                ('contact', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='translations',
                    to='core.sitecontact',
                    verbose_name='İletişim',
                )),
                ('language', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='site_contact_translations',
                    to='localization.language',
                    verbose_name='Dil',
                )),
            ],
            options={
                'verbose_name': 'İletişim çevirisi',
                'verbose_name_plural': 'İletişim çevirileri',
            },
        ),
        migrations.AddConstraint(
            model_name='sitecontacttranslation',
            constraint=models.UniqueConstraint(
                fields=('contact', 'language'),
                name='unique_site_contact_translation_per_language',
            ),
        ),
        migrations.RunPython(migrate_phone_to_contacts, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='sitesettings',
            name='phone',
        ),
    ]
