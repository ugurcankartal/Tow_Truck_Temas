"""Mevcut modeltranslation alanlarından çeviri tablolarına veri taşır."""

from django.db import migrations

SITE_SETTINGS_FIELDS = [
    'meta_title', 'meta_description', 'meta_keywords',
    'business_name', 'legal_name', 'tagline',
    'street', 'district', 'city', 'region',
    'footer_copyright', 'hero_intro_badge', 'hero_intro_title', 'hero_intro_body',
]

FAQ_FIELDS = ['question', 'answer']
STAT_FIELDS = ['value', 'label']
SECTION_FIELDS = ['badge', 'title', 'description']
SERVICE_FIELDS = ['title', 'description']
ZONE_FIELDS = ['name', 'description']
IMAGE_FIELDS = ['title', 'subtitle', 'description', 'alt_text']


def _pick(instance, field, lang_suffix):
    translated = getattr(instance, f'{field}_{lang_suffix}', None)
    if translated not in (None, ''):
        return translated
    return getattr(instance, field, '') or ''


def _lang(apps, code):
    return apps.get_model('localization', 'Language').objects.get(code=code)


def migrate_translations(apps, schema_editor):
    Language = apps.get_model('localization', 'Language')
    if not Language.objects.exists():
        return

    tr = _lang(apps, 'tr')
    en = _lang(apps, 'en')

    SiteSettings = apps.get_model('core', 'SiteSettings')
    SiteSettingsTranslation = apps.get_model('core', 'SiteSettingsTranslation')
    for settings in SiteSettings.objects.all():
        tr_data = {f: _pick(settings, f, 'tr') for f in SITE_SETTINGS_FIELDS}
        tr_data['area_served'] = settings.area_served or []
        SiteSettingsTranslation.objects.update_or_create(
            settings=settings, language=tr, defaults=tr_data,
        )
        en_data = {f: _pick(settings, f, 'en') for f in SITE_SETTINGS_FIELDS}
        en_data['area_served'] = settings.area_served or []
        SiteSettingsTranslation.objects.update_or_create(
            settings=settings, language=en, defaults=en_data,
        )

    FAQ = apps.get_model('core', 'FAQ')
    FAQTranslation = apps.get_model('core', 'FAQTranslation')
    for faq in FAQ.objects.all():
        for lang_obj, suffix in ((tr, 'tr'), (en, 'en')):
            FAQTranslation.objects.update_or_create(
                faq=faq,
                language=lang_obj,
                defaults={f: _pick(faq, f, suffix) for f in FAQ_FIELDS},
            )

    ShowcaseStat = apps.get_model('showcase', 'ShowcaseStat')
    ShowcaseStatTranslation = apps.get_model('showcase', 'ShowcaseStatTranslation')
    for stat in ShowcaseStat.objects.all():
        for lang_obj, suffix in ((tr, 'tr'), (en, 'en')):
            ShowcaseStatTranslation.objects.update_or_create(
                stat=stat,
                language=lang_obj,
                defaults={f: _pick(stat, f, suffix) for f in STAT_FIELDS},
            )

    ShowcaseServiceSection = apps.get_model('showcase', 'ShowcaseServiceSection')
    ShowcaseServiceSectionTranslation = apps.get_model(
        'showcase', 'ShowcaseServiceSectionTranslation',
    )
    for section in ShowcaseServiceSection.objects.all():
        for lang_obj, suffix in ((tr, 'tr'), (en, 'en')):
            ShowcaseServiceSectionTranslation.objects.update_or_create(
                section=section,
                language=lang_obj,
                defaults={f: _pick(section, f, suffix) for f in SECTION_FIELDS},
            )

    ShowcaseService = apps.get_model('showcase', 'ShowcaseService')
    ShowcaseServiceTranslation = apps.get_model('showcase', 'ShowcaseServiceTranslation')
    for service in ShowcaseService.objects.all():
        for lang_obj, suffix in ((tr, 'tr'), (en, 'en')):
            ShowcaseServiceTranslation.objects.update_or_create(
                service=service,
                language=lang_obj,
                defaults={f: _pick(service, f, suffix) for f in SERVICE_FIELDS},
            )

    ContentZone = apps.get_model('content', 'ContentZone')
    ContentZoneTranslation = apps.get_model('content', 'ContentZoneTranslation')
    for zone in ContentZone.objects.all():
        for lang_obj, suffix in ((tr, 'tr'), (en, 'en')):
            ContentZoneTranslation.objects.update_or_create(
                zone=zone,
                language=lang_obj,
                defaults={f: _pick(zone, f, suffix) for f in ZONE_FIELDS},
            )

    SiteImage = apps.get_model('content', 'SiteImage')
    SiteImageTranslation = apps.get_model('content', 'SiteImageTranslation')
    for image in SiteImage.objects.all():
        for lang_obj, suffix in ((tr, 'tr'), (en, 'en')):
            SiteImageTranslation.objects.update_or_create(
                site_image=image,
                language=lang_obj,
                defaults={f: _pick(image, f, suffix) for f in IMAGE_FIELDS},
            )


UI_STRINGS = {
    'tr': {
        'nav.home': 'Ana Sayfa',
        'nav.services': 'Hizmetler',
        'nav.faq': 'SSS',
        'nav.contact': 'İletişim',
        'nav.aria': 'Ana navigasyon',
        'nav.menu_open': 'Menüyü aç',
        'nav.menu_close': 'Menüyü kapat',
        'nav.call_now': 'Hemen Ara',
        'hero.aria': 'Ana tanıtım',
        'hero.slide_select': 'Slayt seçimi',
        'hero.slide_n': 'Slayt',
        'hero.call_now': 'Hemen Arayın',
        'scroll_draw.aria': 'Hizmetler görsel sunum',
        'services.section_aria': 'Hizmetler, SSS ve iletişim',
        'services.faq_badge': 'Sık Sorulan Sorular',
        'services.faq_title': 'Merak Edilenler',
        'services.contact_badge': 'Bize Ulaşın',
        'services.contact_title': 'İletişim Bilgileri',
        'services.phone': 'Telefon',
        'services.email': 'E-posta',
        'services.hours': 'Çalışma Saatleri',
        'services.address': 'Adres',
        'services.phone_hint': '7/24 acil hat — bekletmeden yanıt',
        'services.name': 'Ad Soyad',
        'services.name_placeholder': 'Adınız Soyadınız',
        'services.phone_placeholder': '05XX XXX XX XX',
        'services.message': 'Mesajınız',
        'services.message_placeholder': 'Konum ve araç bilgilerinizi yazın...',
        'services.submit': 'Mesaj Gönder',
        'services.sending': 'Gönderiliyor...',
        'services.success': 'Mesajınız alındı. En kısa sürede dönüş yapacağız.',
        'services.error': 'Form gönderilemedi',
        'services.error_fallback': 'Şu an gönderilemedi. Lütfen doğrudan arayın:',
        'footer.blurb': 'Güvenilir oto çekici ve yol yardım hizmeti. 7/24 hizmetinizdeyiz.',
        'footer.areas_title': 'Hizmet Bölgeleri',
        'footer.contact_title': 'İletişim',
        'footer.phone': 'Telefon',
        'footer.email': 'E-posta',
        'footer.address': 'Adres',
        'footer.hours': 'Çalışma Saatleri',
        'footer.cta_title': 'Acil çekici mi lazım?',
        'footer.cta_subtitle': 'Hemen arayın, ekibimiz yola çıksın.',
    },
    'en': {
        'nav.home': 'Home',
        'nav.services': 'Services',
        'nav.faq': 'FAQ',
        'nav.contact': 'Contact',
        'nav.aria': 'Main navigation',
        'nav.menu_open': 'Open menu',
        'nav.menu_close': 'Close menu',
        'nav.call_now': 'Call Now',
        'hero.aria': 'Hero section',
        'hero.slide_select': 'Slide selection',
        'hero.slide_n': 'Slide',
        'hero.call_now': 'Call Now',
        'scroll_draw.aria': 'Services visual showcase',
        'services.section_aria': 'Services, FAQ and contact',
        'services.faq_badge': 'Frequently Asked Questions',
        'services.faq_title': 'Common Questions',
        'services.contact_badge': 'Get in Touch',
        'services.contact_title': 'Contact Information',
        'services.phone': 'Phone',
        'services.email': 'Email',
        'services.hours': 'Opening Hours',
        'services.address': 'Address',
        'services.phone_hint': '24/7 emergency line — no waiting',
        'services.name': 'Full Name',
        'services.name_placeholder': 'Your full name',
        'services.phone_placeholder': '+90 5XX XXX XX XX',
        'services.message': 'Your Message',
        'services.message_placeholder': 'Location and vehicle details...',
        'services.submit': 'Send Message',
        'services.sending': 'Sending...',
        'services.success': 'Your message has been received. We will get back to you shortly.',
        'services.error': 'Could not send the form',
        'services.error_fallback': 'Could not send right now. Please call directly:',
        'footer.blurb': 'Reliable tow truck and roadside assistance. Available 24/7.',
        'footer.areas_title': 'Service Areas',
        'footer.contact_title': 'Contact',
        'footer.phone': 'Phone',
        'footer.email': 'Email',
        'footer.address': 'Address',
        'footer.hours': 'Opening Hours',
        'footer.cta_title': 'Need emergency towing?',
        'footer.cta_subtitle': 'Call now and our team will be on the way.',
    },
}


def seed_ui_strings(apps, schema_editor):
    Language = apps.get_model('localization', 'Language')
    UiStringKey = apps.get_model('localization', 'UiStringKey')
    UiString = apps.get_model('localization', 'UiString')
    for lang_code, strings in UI_STRINGS.items():
        language = Language.objects.filter(code=lang_code).first()
        if not language:
            continue
        for key, text in strings.items():
            key_obj, _ = UiStringKey.objects.get_or_create(key=key)
            UiString.objects.update_or_create(
                language=language,
                key=key_obj,
                defaults={'text': text},
            )


def forwards(apps, schema_editor):
    migrate_translations(apps, schema_editor)
    seed_ui_strings(apps, schema_editor)


class Migration(migrations.Migration):

    dependencies = [
        ('localization', '0002_seed_languages'),
        ('core', '0012_sitesettings_faq_translations'),
        ('content', '0004_content_translations'),
        ('showcase', '0004_showcase_translations'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
