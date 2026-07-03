from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('localization', '0003_migrate_content_translations'),
        ('showcase', '0004_showcase_translations'),
    ]

    operations = [
        migrations.RemoveField(model_name='showcaseservice', name='description_en'),
        migrations.RemoveField(model_name='showcaseservice', name='description_tr'),
        migrations.RemoveField(model_name='showcaseservice', name='title_en'),
        migrations.RemoveField(model_name='showcaseservice', name='title_tr'),
        migrations.RemoveField(model_name='showcaseservicesection', name='badge_en'),
        migrations.RemoveField(model_name='showcaseservicesection', name='badge_tr'),
        migrations.RemoveField(model_name='showcaseservicesection', name='description_en'),
        migrations.RemoveField(model_name='showcaseservicesection', name='description_tr'),
        migrations.RemoveField(model_name='showcaseservicesection', name='title_en'),
        migrations.RemoveField(model_name='showcaseservicesection', name='title_tr'),
        migrations.RemoveField(model_name='showcasestat', name='label_en'),
        migrations.RemoveField(model_name='showcasestat', name='label_tr'),
        migrations.RemoveField(model_name='showcasestat', name='value_en'),
        migrations.RemoveField(model_name='showcasestat', name='value_tr'),
    ]
