from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_sitesettings_faq_translations'),
        ('localization', '0003_migrate_content_translations'),
    ]

    operations = [
        migrations.RemoveField(model_name='faq', name='answer_en'),
        migrations.RemoveField(model_name='faq', name='answer_tr'),
        migrations.RemoveField(model_name='faq', name='question_en'),
        migrations.RemoveField(model_name='faq', name='question_tr'),
        migrations.RemoveField(model_name='sitesettings', name='business_name_en'),
        migrations.RemoveField(model_name='sitesettings', name='business_name_tr'),
        migrations.RemoveField(model_name='sitesettings', name='city_en'),
        migrations.RemoveField(model_name='sitesettings', name='city_tr'),
        migrations.RemoveField(model_name='sitesettings', name='district_en'),
        migrations.RemoveField(model_name='sitesettings', name='district_tr'),
        migrations.RemoveField(model_name='sitesettings', name='footer_copyright_en'),
        migrations.RemoveField(model_name='sitesettings', name='footer_copyright_tr'),
        migrations.RemoveField(model_name='sitesettings', name='hero_intro_badge_en'),
        migrations.RemoveField(model_name='sitesettings', name='hero_intro_badge_tr'),
        migrations.RemoveField(model_name='sitesettings', name='hero_intro_body_en'),
        migrations.RemoveField(model_name='sitesettings', name='hero_intro_body_tr'),
        migrations.RemoveField(model_name='sitesettings', name='hero_intro_title_en'),
        migrations.RemoveField(model_name='sitesettings', name='hero_intro_title_tr'),
        migrations.RemoveField(model_name='sitesettings', name='legal_name_en'),
        migrations.RemoveField(model_name='sitesettings', name='legal_name_tr'),
        migrations.RemoveField(model_name='sitesettings', name='meta_description_en'),
        migrations.RemoveField(model_name='sitesettings', name='meta_description_tr'),
        migrations.RemoveField(model_name='sitesettings', name='meta_keywords_en'),
        migrations.RemoveField(model_name='sitesettings', name='meta_keywords_tr'),
        migrations.RemoveField(model_name='sitesettings', name='meta_title_en'),
        migrations.RemoveField(model_name='sitesettings', name='meta_title_tr'),
        migrations.RemoveField(model_name='sitesettings', name='region_en'),
        migrations.RemoveField(model_name='sitesettings', name='region_tr'),
        migrations.RemoveField(model_name='sitesettings', name='street_en'),
        migrations.RemoveField(model_name='sitesettings', name='street_tr'),
        migrations.RemoveField(model_name='sitesettings', name='tagline_en'),
        migrations.RemoveField(model_name='sitesettings', name='tagline_tr'),
    ]
