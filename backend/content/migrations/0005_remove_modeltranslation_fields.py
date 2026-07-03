from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0004_content_translations'),
        ('localization', '0003_migrate_content_translations'),
    ]

    operations = [
        migrations.RemoveField(model_name='contentzone', name='description_en'),
        migrations.RemoveField(model_name='contentzone', name='description_tr'),
        migrations.RemoveField(model_name='contentzone', name='name_en'),
        migrations.RemoveField(model_name='contentzone', name='name_tr'),
        migrations.RemoveField(model_name='siteimage', name='alt_text_en'),
        migrations.RemoveField(model_name='siteimage', name='alt_text_tr'),
        migrations.RemoveField(model_name='siteimage', name='description_en'),
        migrations.RemoveField(model_name='siteimage', name='description_tr'),
        migrations.RemoveField(model_name='siteimage', name='subtitle_en'),
        migrations.RemoveField(model_name='siteimage', name='subtitle_tr'),
        migrations.RemoveField(model_name='siteimage', name='title_en'),
        migrations.RemoveField(model_name='siteimage', name='title_tr'),
    ]
