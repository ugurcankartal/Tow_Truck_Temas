from django.db import migrations


def seed_languages(apps, schema_editor):
    Language = apps.get_model('localization', 'Language')
    for code, name_native, is_default, sort_order in [
        ('tr', 'Türkçe', True, 1),
        ('en', 'English', False, 2),
    ]:
        Language.objects.get_or_create(
            code=code,
            defaults={
                'name_native': name_native,
                'is_active': True,
                'is_default': is_default,
                'sort_order': sort_order,
            },
        )


def unseed_languages(apps, schema_editor):
    Language = apps.get_model('localization', 'Language')
    Language.objects.filter(code__in=['tr', 'en']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('localization', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_languages, unseed_languages),
    ]
